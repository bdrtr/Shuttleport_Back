"""
Admin panel configuration using SQLAdmin - User-friendly version
"""
from sqladmin import Admin, ModelView
from app.database import engine
from app.models.db_models import Vehicle, FixedRoute, PricingConfig


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
        "active": "Active"
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class FixedRouteAdmin(ModelView, model=FixedRoute):
    """Admin view for fixed routes"""
    name = "Fixed Route"
    name_plural = "Fixed Routes"
    icon = "fa-solid fa-route"
    
    # Show route info - don't use formatters to avoid errors
    column_list = ["id", "origin", "destination", "price", "active"]
    
    column_searchable_list = ["origin", "destination"]
    column_sortable_list = ["id", "origin", "destination", "price", "active"]
    column_default_sort = ("id", False)
    
    # Better labels - vehicle shown in details/edit
    column_labels = {
        "id": "Route ID",
        "origin": "From",
        "destination": "To",
        "vehicle_id": "Vehicle Type",
        "price": "Price (₺)",
        "discount_percent": "Discount %",
        "competitor_price": "Competitor Price",
        "notes": "Notes",
        "active": "Active"
    }
    
    # Pagination
    page_size = 25
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


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
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


def setup_admin(app):
    """Initialize and configure the admin panel"""
    admin = Admin(
        app,
        engine,
        title="Shuttleport Admin",
        base_url="/admin"
    )
    
    # Register admin views
    admin.add_view(VehicleAdmin)
    admin.add_view(FixedRouteAdmin)
    admin.add_view(PricingConfigAdmin)
    
    return admin
