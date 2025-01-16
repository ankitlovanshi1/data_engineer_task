import yaml
import os


class TemplateUpdater:
    def __init__(self, template_path, min_runtime="python3.9"):
        self.template_path = template_path
        self.min_runtime = min_runtime

    def load_template(self):
        """Load the YAML content from the template.yaml file with custom tag handling."""
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"Error: {self.template_path} does not exist.")

        # Add custom constructor to ignore unsupported tags like !Sub
        def custom_constructor(loader, tag_suffix, node):
            return loader.construct_scalar(node)

        yaml.SafeLoader.add_multi_constructor("!", custom_constructor)

        with open(self.template_path, "r") as file:
            try:
                return yaml.safe_load(file)
            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing YAML file: {e}")

    def update_runtime(self, content):
        updated = False
        if "Resources" in content:
            for resource, details in content["Resources"].items():
                if isinstance(details, dict) and "Properties" in details:
                    properties = details["Properties"]
                    if "Runtime" in properties:
                        current_runtime = properties["Runtime"]
                        if current_runtime <= "python3.8":
                            print(
                                f"Updating Runtime for resource '{resource}' from {current_runtime} to {self.min_runtime}"
                            )
                            properties["Runtime"] = self.min_runtime
                            updated = True
        return updated

    def save_template(self, content):
        """Save the updated YAML content back to the template.yaml file."""
        with open(self.template_path, "w") as file:
            yaml.safe_dump(content, file)
        print("Template saved successfully.")

    def process_template(self):
        """Main method to process the template.yaml file."""
        try:
            content = self.load_template()
            if self.update_runtime(content):
                self.save_template(content)
                print("Runtime updated successfully.")
            else:
                print("No Runtime updates were necessary.")
        except Exception as e:
            print(str(e))


if __name__ == "__main__":
    # Path to the template.yaml file
    template_path = "/home/developer/Documents/Data_Engineering/sam-python-crud-sample/template.yaml" 

    updater = TemplateUpdater(template_path)
    updater.process_template()
