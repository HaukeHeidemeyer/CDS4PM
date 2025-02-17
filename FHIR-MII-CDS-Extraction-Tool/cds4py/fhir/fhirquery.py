class FHIRQueryURLBuilder:
    def __init__(self, base_url):
        self.base_url = base_url
        self.query_parts = []

    def add_query_part(self, part):
        if part:
            self.query_parts.append(part)

    def include_resource(self, resource_name, reference):
        self.query_parts.append(f"_include={resource_name}:{reference}")

    def rev_include_resource(self, resource_name, reference):
        self.query_parts.append(f"_revinclude={resource_name}:{reference}")

    def build_url(self):
        query_string = "&".join(self.query_parts)
        return f"{self.base_url}/Encounter?{query_string}"
