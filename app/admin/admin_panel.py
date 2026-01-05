"""
Admin panel configuration using SQLAdmin - User-friendly version
"""
import shutil
import os
from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqladmin import Admin, ModelView, BaseView, expose
from markupsafe import Markup
from wtforms import SelectField, SelectMultipleField, widgets
from app.database import engine, SessionLocal
from app.models.db_models import Vehicle, VehicleImage, FixedRoute, PricingConfig
from app.core.constants import VEHICLE_TYPES, ISTANBUL_LOCATIONS, FEATURE_DEFINITIONS, FEATURE_CHOICES
from app.services.data_manager import DataManager
from app.services.init_db import init_routes_data




class VehicleImageAdmin(ModelView, model=VehicleImage):
    """Admin view for vehicle images"""
    name = "Vehicle Image"
    name_plural = "Vehicle Images"
    icon = "fa-solid fa-images"
    
    column_list = ["id", "vehicle", "image_path", "is_primary", "created_at"]
    column_sortable_list = ["id", "vehicle", "created_at"]
    
    column_labels = {
        "vehicle": "Vehicle",
        "image_path": "Image",
        "is_primary": "Primary Image",
        "display_order": "Display Order"
    }
    
    # Format image_path to show thumbnail
    column_formatters = {
        "image_path": lambda m, a: Markup(f'<img src="/static/{m.image_path}" style="max-width: 100px; max-height: 60px; object-fit: cover; border-radius: 4px;">') if m.image_path else Markup('<span style="color: #999;">No image</span>')
    }
    
    form_columns = ["vehicle", "image_path", "is_primary"]
    
    # Use our standard ImageUploadField
    from app.admin.utils import ImageUploadField
    
    form_overrides = {
        "image_path": ImageUploadField
    }
    
    form_args = {
        "image_path": {
            "label": "Upload Image",
            "base_path": "static/images",
            "relative_path": "images"
        }
    }
    
    
    async def insert_model(self, request, data):
        """Called when inserting a new model - handle multiple file uploads"""
        # Check if multiple files were uploaded
        if "image_path" in data:
            image_files = data["image_path"]
            
            # If it's a list (multiple files), create a record for each
            if isinstance(image_files, list) and len(image_files) > 0:
                # Extract vehicle_id - SQLAdmin might send it as 'vehicle' (the object) or 'vehicle_id'
                vehicle_id = data.get("vehicle_id")
                if vehicle_id is None and "vehicle" in data:
                    # If vehicle is an object, get its id
                    vehicle = data.get("vehicle")
                    if hasattr(vehicle, "id"):
                        vehicle_id = vehicle.id
                    else:
                        vehicle_id = vehicle  # It's already an ID
                
                is_primary = data.get("is_primary", False)
                created_images = []
                
                from app.database import SessionLocal
                from app.models.db_models import VehicleImage
                db = SessionLocal()
                
                try:
                    # Create a record for each uploaded file
                    for idx, image_file in enumerate(image_files):
                        # Process each file
                        file_data = {
                            "vehicle_id": vehicle_id,
                            "image_path": image_file,
                            "is_primary": is_primary if idx == 0 else False  # Only first one primary if checked
                        }
                        
                        # Handle file upload for this specific file
                        await self._handle_file_upload(file_data)
                        
                        # Handle primary logic for this file
                        if file_data.get("is_primary"):
                            await self._handle_primary_image(file_data, is_new=True)
                        
                        # Create the record
                        if "image_path" in file_data:  # File was successfully processed
                            obj = VehicleImage(**file_data)
                            db.add(obj)
                            created_images.append(obj)
                    
                    db.commit()
                    for obj in created_images:
                        db.refresh(obj)
                    
                    print(f"✓ Created {len(created_images)} image records")
                    
                    # Return first one (SQLAdmin expects a single object)
                    return created_images[0] if created_images else None
                    
                except Exception as e:
                    db.rollback()
                    print(f"ERROR in multi-file insert: {e}")
                    raise e
                finally:
                    db.close()
            else:
                # Single file - use original flow
                await self._handle_file_upload(data)
                await self._handle_primary_image(data, is_new=True)
                return await super().insert_model(request, data)
        else:
            # No file - use original flow
            return await super().insert_model(request, data)
    
    async def update_model(self, request, pk, data):
        """Called when updating an existing model - intercept here to handle file upload"""
        await self._handle_file_upload(data)
        await self._handle_primary_image(data, is_new=False, current_id=pk)
        # Call parent's update method
        return await super().update_model(request, pk, data)
    
    async def _handle_file_upload(self, data: dict):
        """Process file upload and replace UploadFile with string path"""
        if "image_path" not in data:
            return
        
        image_file = data["image_path"]
        
        # If already a string path, skip
        if isinstance(image_file, str):
            return
        
        # Check if it's a file upload object
        if not hasattr(image_file, "filename"):
            return
        
        filename = image_file.filename
        
        # Empty file, remove from data
        if not filename:
            del data["image_path"]
            return
        
        try:
            import os
            from uuid import uuid4
            
            # Generate unique filename
            file_extension = os.path.splitext(filename)[1].lower()
            unique_filename = f"{uuid4()}{file_extension}"
            
            # Ensure directory exists
            os.makedirs("static/images", exist_ok=True)
            
            # Save file
            file_location = f"static/images/{unique_filename}"
            
            # Read file content (works with both UploadFile and FileStorage)
            if hasattr(image_file, 'read'):
                # UploadFile (async)
                content = await image_file.read()
            elif hasattr(image_file, 'file'):
                # FileStorage (sync)
                content = image_file.file.read()
            else:
                print(f"ERROR: Unknown file type: {type(image_file)}")
                del data["image_path"]
                return
            
            # Write to disk
            with open(file_location, "wb") as f:
                f.write(content)
            
            # Update data with string path
            data["image_path"] = f"images/{unique_filename}"
            print(f"✓ Image saved: {file_location}")
            
        except Exception as e:
            print(f"ERROR saving image: {e}")
            import traceback
            traceback.print_exc()
            # Remove to prevent DB error
            if "image_path" in data:
                del data["image_path"]
    
    async def _handle_primary_image(self, data: dict, is_new: bool, current_id=None):
        """Ensure only one primary image per vehicle"""
        # If this image is being marked as primary
        if data.get("is_primary", False):
            # Extract vehicle_id 
            vehicle_id = data.get("vehicle_id")
            if vehicle_id is None and "vehicle" in data:
                vehicle = data.get("vehicle")
                if hasattr(vehicle, "id"):
                    vehicle_id = vehicle.id
                else:
                    vehicle_id = vehicle
            
            if vehicle_id:
                # Unmark all other images for this vehicle
                from app.database import SessionLocal
                db = SessionLocal()
                try:
                    # Get all images for this vehicle
                    from app.models.db_models import VehicleImage
                    
                    if is_new:
                        # For new images, unmark all existing ones
                        db.query(VehicleImage).filter(
                            VehicleImage.vehicle_id == vehicle_id
                        ).update({"is_primary": False})
                    else:
                        # For updates, unmark all except current
                        db.query(VehicleImage).filter(
                            VehicleImage.vehicle_id == vehicle_id,
                            VehicleImage.id != current_id
                        ).update({"is_primary": False})
                    
                    db.commit()
                    print(f"✓ Set image as primary for vehicle {vehicle_id}")
                except Exception as e:
                    print(f"ERROR in _handle_primary_image: {e}")
                    db.rollback()
                finally:
                    db.close()
    
    can_create = True
    can_edit = True
    can_delete = True




class CheckboxListWidget(widgets.ListWidget):
    """Custom widget to render checkboxes cleanly without theme interference"""
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = [f'<{self.html_tag} id="{field.id}" style="list-style: none; padding: 0; margin: 0;">']
        for subfield in field:
            # Force style to prevent 'form-control' stretching and ensure native clickability
            # Important: Admin templates often hide checkboxes (opacity:0) for custom styling (iCheck).
            # We must override this with !important to keep them visible and clickable.
            cb_style = (
                "width: 20px; height: 20px; display: inline-block; vertical-align: middle; margin-right: 8px; "
                "appearance: checkbox !important; -webkit-appearance: checkbox !important; "
                "opacity: 1 !important; position: static !important; pointer-events: auto !important; cursor: pointer;"
            )
            cb = subfield(style=cb_style)
            label = subfield.label(style="display: inline-block; vertical-align: middle; font-weight: normal; margin-bottom: 0; cursor: pointer;")
            html.append(f'<li style="margin-bottom: 8px; display: flex; align-items: center;">{cb} {label}</li>')
        html.append(f'</{self.html_tag}>')
        return Markup(''.join(html))

class JsonFeatureField(SelectMultipleField):
    """Custom field to handle conversion between JSON list of dicts and list of keys"""
    widget = CheckboxListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
    
    def process_data(self, value):
        """Convert Model Data (JSON) -> Form Data (List of Keys)"""
        if not value or not isinstance(value, list):
            self.data = []
            return

        text_to_key = {}
        for k, v in FEATURE_DEFINITIONS.items():
            text_to_key[v[1]] = k
        
        selected_keys = []
        for item in value:
            if isinstance(item, dict) and "text" in item:
                text = item["text"]
                if text in text_to_key:
                    selected_keys.append(text_to_key[text])
        
        self.data = selected_keys

    def populate_obj(self, obj, name):
        formatted_features = []
        if self.data:
            for key in self.data:
                if key in FEATURE_DEFINITIONS:
                    icon, text = FEATURE_DEFINITIONS[key]
                    formatted_features.append({"icon": icon, "text": text})
        setattr(obj, name, formatted_features)


class VehicleAdmin(ModelView, model=Vehicle):
    """Admin view for vehicles"""
    name = "Vehicle"
    name_plural = "Vehicles"
    icon = "fa-solid fa-car"
    
    # Show ID and name together in list
    column_list = ["id", "name_en", "vehicle_type", "capacity_max", "active"]
    column_searchable_list = ["name_en", "name_tr", "vehicle_type"]
    column_sortable_list = ["id", "name_en", "active"]
    column_default_sort = ("id", False)
    
    # Better labels
    column_labels = {
        "id": "ID",
        "name_en": "Vehicle Name",
        "vehicle_type": "Type Code",
        "capacity_max": "Capacity",
        "active": "Active",
        "image_path": "Image",
        "images": "Gallery",
        "base_multiplier": "Base Multiplier (TL)"
    }
    
    # Format images relationship to show thumbnails
    column_formatters = {
        "images": lambda m, a: Markup('<div style="display: flex; gap: 5px; flex-wrap: wrap;">' + 
            ''.join([f'<img src="/static/{img.image_path}" style="max-width: 80px; max-height: 50px; object-fit: cover; border-radius: 4px; border: 2px solid {"#4CAF50" if img.is_primary else "#ddd"};" title="{"Primary" if img.is_primary else ""}">' 
                    for img in (m.images or [])]) + 
            '</div>') if m.images else Markup('<span style="color: #999;">No images</span>'),
        
        "fixed_routes": lambda m, a: Markup(
            '<table style="width: 100%; border-collapse: collapse; font-size: 0.9em;">'
            '<thead><tr style="background: #f5f5f5;">'
            '<th style="padding: 6px; text-align: left; border-bottom: 2px solid #ddd;">Route</th>'
            '<th style="padding: 6px; text-align: right; border-bottom: 2px solid #ddd;">Price</th>'
            '<th style="padding: 6px; text-align: center; border-bottom: 2px solid #ddd;">Status</th>'
            '</tr></thead><tbody>' +
            ''.join([
                f'<tr style="border-bottom: 1px solid #eee;">'
                f'<td style="padding: 6px;"><b>{route.origin}</b> → <b>{route.destination}</b></td>'
                f'<td style="padding: 6px; text-align: right; color: #2196F3; font-weight: bold;">{route.price:,.2f} ₺</td>'
                f'<td style="padding: 6px; text-align: center;">{"✅" if route.active else "❌"}</td>'
                f'</tr>'
                for route in (m.fixed_routes or [])
            ]) +
            '</tbody></table>'
        ) if m.fixed_routes else Markup('<span style="color: #999;">No fixed routes</span>')
    }

    # Form configuration
    form_columns = [
        "vehicle_type", "name_en", "name_tr", 
        "capacity_min", "capacity_max", "baggage_capacity",
        "base_multiplier", "features", "active"
    ]
    
    form_overrides = {
        "vehicle_type": SelectField,
        "features": JsonFeatureField
    }
    
    form_args = {
        "vehicle_type": {
            "choices": VEHICLE_TYPES,
            "label": "Araç Tipi (Type Code)"
        },
        "features": {
            "choices": FEATURE_CHOICES,
            "label": "Araç Özellikleri (Features)",
            "default": list(FEATURE_DEFINITIONS.keys())
        }
    }


class FixedRouteAdmin(ModelView, model=FixedRoute):
    """Admin view for fixed routes"""
    name = "Fixed Route"
    name_plural = "Fixed Routes"
    icon = "fa-solid fa-route"
    identity = "fixed_route"
    list_template = "fixed_route_list.html"
    
    # Show route info with vehicle
    column_list = ["id", "origin", "destination", "vehicle", "price", "active"]
    
    column_searchable_list = ["origin", "destination"]
    column_sortable_list = ["id", "origin", "destination", "price", "active"]
    column_default_sort = ("id", False)
    
    # Format vehicle to show name instead of object
    column_formatters = {
        "vehicle": lambda m, a: Markup(f'<span title="Type: {m.vehicle.vehicle_type}">{m.vehicle.name_en}</span>') if m.vehicle else Markup('<span style="color: #999;">No vehicle</span>')
    }
    
    # Better labels - vehicle shown in details/edit
    column_labels = {
        "id": "Route ID",
        "origin": "From (Kalkış)",
        "destination": "To (Varış)",
        "vehicle": "Vehicle",
        "vehicle_id": "Vehicle Type",
        "price": "Price (₺)",
        "discount_percent": "Discount %",
        "competitor_price": "Competitor Price",
        "notes": "Notes",
        "active": "Active"
    }
    
    # Use Dropdowns for Location Fields
    from wtforms import SelectField
    
    form_overrides = {
        "origin": SelectField,
        "destination": SelectField
    }
    
    form_args = {
        "origin": {
            "choices": ISTANBUL_LOCATIONS,
            "label": "From (Kalkış Noktası)"
        },
        "destination": {
            "choices": ISTANBUL_LOCATIONS,
            "label": "To (Varış Noktası)"
        }
    }
    
    # Pagination
    page_size = 25
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    async def insert_model(self, request, data):
        try:
            return await super().insert_model(request, data)
        except Exception as e:
            # Check for unique constraint violation
            error_str = str(e).lower()
            if "unique constraint" in error_str or "duplicate key" in error_str:
                # User friendly error
                raise Exception(f"Error: A route for {data.get('origin')} -> {data.get('destination')} with this vehicle already exists.")
            raise e

    async def update_model(self, request, pk, data):
        try:
            return await super().update_model(request, pk, data)
        except Exception as e:
             # Check for unique constraint violation
            error_str = str(e).lower()
            if "unique constraint" in error_str or "duplicate key" in error_str:
                # User friendly error
                raise Exception(f"Error: A route for {data.get('origin')} -> {data.get('destination')} with this vehicle already exists.")
            raise e


class PricingConfigAdmin(ModelView, model=PricingConfig):
    """Admin view for pricing configuration"""
    name = "Pricing Config"
    name_plural = "Pricing Configurations"
    icon = "fa-solid fa-gear"
    
    # Show key and description together
    column_list = ["id", "config_key", "config_value", "description"]
    column_searchable_list = ["config_key", "description"]
    column_sortable_list = ["id", "config_key", "config_value"]
    column_default_sort = ("config_key", False)
    
    # Better labels
    column_labels = {
        "id": "Config ID",
        "config_key": "Setting Name",
        "config_value": "Value (₺ or %)",
        "description": "Description",
        "vehicle_type": "Vehicle Type"
    }

    form_overrides = {
        "vehicle_type": SelectField
    }
    
    form_args = {
        "vehicle_type": {
            "choices": [(None, "Genel / Tüm Araçlar (Global)")] + VEHICLE_TYPES,
            "label": "Vehicle Type"
        }
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True



def setup_admin(app):
    """Initialize and configure the admin panel"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, "templates")
    
    admin = Admin(
        app,
        engine,
        title="Shuttleport Admin",
        base_url="/admin",
        templates_dir=templates_dir
    )
    
    # Register admin views
    admin.add_view(VehicleAdmin)
    admin.add_view(VehicleImageAdmin)
    admin.add_view(FixedRouteAdmin)
    admin.add_view(PricingConfigAdmin)
    
    return admin
