"""
Admin panel configuration using SQLAdmin - Simplified version
"""
from sqladmin import Admin, ModelView
from app.database import engine
from app.models.db_models import Vehicle, FixedRoute, PricingConfig


class VehicleAdmin(ModelView, model=Vehicle):
    """Admin view for vehicles"""
    name = "Vehicle"
    name_plural = "Vehicles"
    icon = "fa-solid fa-car"
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class FixedRouteAdmin(ModelView, model=FixedRoute):
    """Admin view for fixed routes"""
    name = "Fixed Route"
    name_plural = "Fixed Routes"
    icon = "fa-solid fa-route"
    
    # Minimal configuration - let SQLAdmin auto-detect most things
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
