import os
import secrets
from wtforms import FileField
from wtforms.widgets import FileInput

class MultipleFileInput(FileInput):
    """Custom file input widget that allows multiple file selection"""
    def __call__(self, field, **kwargs):
        kwargs['multiple'] = True
        return super().__call__(field, **kwargs)

class ImageUploadField(FileField):
    """
    Custom WTForms field that handles image uploads,
    saves them to a specific directory, and returns the filename.
    """
    widget = MultipleFileInput()

    def __init__(self, label=None, validators=None, base_path="static", relative_path="images", target_column=None, **kwargs):
        super(ImageUploadField, self).__init__(label, validators, **kwargs)
        self.base_path = base_path
        self.relative_path = relative_path
        self.target_column = target_column

    def process_formdata(self, valuelist):
        if valuelist:
            # If multiple files selected, return all of them
            # Otherwise return single file (backward compatible)
            if len(valuelist) > 1:
                self.data = valuelist
            else:
                self.data = valuelist[0]
        else:
            self.data = None

    def populate_obj(self, obj, name):
        """
        Called when populating the model from the form.
        Saves the file and sets the filename on the model.
        """
        print(f"DEBUG: ImageUploadField.populate_obj called for {name}")
        if self.data and hasattr(self.data, "filename"):
            print(f"DEBUG: Processing file {self.data.filename}")
            # Generate a secure filename
            filename = self.data.filename
            ext = os.path.splitext(filename)[1].lower()
            
            # Use random name to avoid collisions
            safe_filename = secrets.token_hex(8) + ext
            
            # Ensure directory exists
            full_dir = os.path.join(self.base_path)
            os.makedirs(full_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(full_dir, safe_filename)
            with open(file_path, "wb") as f:
                f.write(self.data.file.read())
            
            # Save request relative path to model (e.g. "images/filename.jpg")
            db_path = f"{self.relative_path}/{safe_filename}" if self.relative_path else safe_filename
            
            # If target column specified, use that, otherwise use field name
            target = self.target_column if self.target_column else name
            setattr(obj, target, db_path)


from wtforms import MultipleFileField

class MultiImageUploadField(MultipleFileField):
    """
    Custom WTForms field that handles multiple image uploads,
    saves them to a specific directory, and returns a list of filenames/paths.
    """
    def __init__(self, label=None, validators=None, base_path="static", relative_path="images", target_column=None, **kwargs):
        super(MultiImageUploadField, self).__init__(label, validators, **kwargs)
        self.base_path = base_path
        self.relative_path = relative_path
        self.target_column = target_column

    def process_formdata(self, valuelist):
        if valuelist:
            # valuelist is a list of FileStorage objects
            self.data = valuelist
        else:
            self.data = []

    def populate_obj(self, obj, name):
        """
        Called when populating the model from the form.
        Saves the files and sets the list of paths on the model.
        """
        if self.data:
            print("MultiImageUploadField: Processing upload data...")
            preserved_paths = []
            
            # Ensure directory exists
            full_dir = os.path.join(self.base_path)
            os.makedirs(full_dir, exist_ok=True)
            
            for file_storage in self.data:
                # Skip empty files (if any)
                if not getattr(file_storage, 'filename', None):
                    continue
                
                filename = file_storage.filename
                ext = os.path.splitext(filename)[1].lower()
                safe_filename = secrets.token_hex(8) + ext
                
                # Save file
                file_path = os.path.join(full_dir, safe_filename)
                with open(file_path, "wb") as f:
                    f.write(file_storage.read())
                
                # Determine request relative path
                db_path = f"{self.relative_path}/{safe_filename}" if self.relative_path else safe_filename
                preserved_paths.append(db_path)
            
            # If we have new files, append to existing images if possible or overwrite?
            # Usually multi-upload replaces or appends. 
            # Ideally we want to Keep existing, but WTForms populate_obj can be tricky with lists.
            # Let's simple OVERWRITE for now, or Append if data is existing.
            
            # If existing data is a list, extend it?
            # But the user might want to clear. 
            # Typical admin behavior: If I upload new files, they are Added.
            # But we need a way to delete. 
            # For MVP: New uploads are appended to the list.
            
            target = self.target_column if self.target_column else name
            raw_existing = getattr(obj, target, []) or []
            if not isinstance(raw_existing, list):
                existing_images = []
            else:
                # Sanitize: Remove any UploadFile objects that might have been auto-assigned
                # Only keep strings (paths)
                existing_images = [img for img in raw_existing if isinstance(img, str)]
                
            updated_images = existing_images + preserved_paths
            print(f"MultiImageUploadField: Saving {updated_images} to {target}")
            setattr(obj, target, updated_images)
