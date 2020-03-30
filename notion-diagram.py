import json
import subprocess
from notion.client import NotionClient
from notion.block import ImageBlock
from notion.block import FileBlock
from notion.block import ToggleBlock

def fmt_owners(owners):
    names=""
    for owner in owners:
        names+=owner.full_name
    return names

def fmt_task(origin, task):
    status_to_color = {'Done': "#green", 'In Progress': "#yellow", 'None': "#gray"}
    return ("note over \"{}\" {}: {}\\nStatus {}\\nOwners: {}\\n[[{} Task]]\n"
            .format(origin,
                    status_to_color[task.status],
                    task.title,
                    task.status,
                    fmt_owners(task.owners),
                    task.get_browseable_url()))

def puml_diagram(client):
    sequence_diagram_table_url = "https://www.notion.so/fb2e7fa7fb6e4f2f846f30982a9bb6a8?v=d4e26755d6004a55a52fc463756a28be"
    pum = "@startuml\n"
    cv = client.get_collection_view(sequence_diagram_table_url)
    for row in cv.collection.get_rows():
        service_origin_block = row.origin[0]
        service_end_block = row.end[0]
        pum+=("\"{}\" -> \"{}\": {}\n".format(service_origin_block.name,
                                              service_end_block.name,
                                              row.label))
        for task in row.task:
            pum+=fmt_task(service_origin_block.name, task)
    pum+="@enduml"
    return pum

def write_files(diagram, client):
    print(diagram, file=open('out.puml', 'w'))
    subprocess.Popen(["java", "-jar", "plantuml.jar", "-tsvg", "out.puml"])
    subprocess.Popen(["java", "-jar", "plantuml.jar", "-tpng", "out.puml"])

# TODO: Remove existing blocks rather than appending new ones
def upload_to_notion(client):
    sequence_diagrams_page_url = "https://www.notion.so/sequence-diagrams-in-notion-tasks-018a03174e454e69919ba903169623bf"
    page = client.get_block(sequence_diagrams_page_url)
    image = page.children.add_new(ImageBlock)
    image.upload_file("out.png")
    svg_file = page.children.add_new(FileBlock)
    svg_file.upload_file("out.svg")

def client():
    token = ""
    with open('config.json', 'r') as f:
        token = json.load(f)['token']
    return NotionClient(token_v2=token)

client = client()
write_files(puml_diagram(client), client)
upload_to_notion(client)
