import os
import logging
import xmltodict

logging.basicConfig(level=logging.DEBUG)

main_folder = "D:\\FIFA Edit\\Blender\\stadium_workspace\\Worlds\\Components"

class Position:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class CrowdPoint:
    def __init__(self, position, card_color, seat_color, seat_tier, home_away_neutral, home_away_ultra, home_away_fifty_fifty, attendance, orientation):
        self.position = position
        self.card_color = card_color
        self.seat_color = seat_color
        self.seat_tier = seat_tier
        self.home_away_neutral = home_away_neutral
        self.home_away_ultra = home_away_ultra
        self.home_away_fifty_fifty = home_away_fifty_fifty
        self.attendance = attendance
        self.orientation = orientation

class CrowdData:
    def __init__(self, crowd_points):
        if not all(isinstance(crowd_point, CrowdPoint) for crowd_point in crowd_points):
            raise ValueError("All elements in the list must be CrowdPoint instances")
        self.crowd_points = crowd_points


def find_parent_by_child_value(root, element_type, child_tag, child_value):
    nbiterations = 0
    for element in root.findall(f'.//{element_type}'):
        child = element.find(child_tag)
        logging.debug(f"iteration {nbiterations}, name is {child.text if child is not None else "EMPTY"}")
        if child is not None and child.text == child_value:
            return element
    return None


def parse_user_data(element, count):
    values = []
    for i in range(count):
        member = element.find(f'val/member[{i+1}]')
        values.append(member.text if member is not None else None)
    return values

def hex_to_rgba(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 8:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4, 6))
    raise ValueError("Input should be a 8-character hex string")



def deserialize_crowd_points(xml_file_path):
    with open(xml_file_path, 'r') as file:
        xml_content = file.read()
    
    wrapped_xml_content = f"<Root>{xml_content}</Root>"
    xml_data = xmltodict.parse(wrapped_xml_content)
    
    vec3_data = xml_data['Root']['CrowdPlacementPointCloudDataAsset']['Data']['member']

    card_color_section = next(sec['val']['member'] for sec in xml_data['Root']['UserDataUintMap'] if sec['Name'] == 'CardColor')
    seat_color_section = next(sec['val']['member'] for sec in xml_data['Root']['UserDataUintMap'] if sec['Name'] == 'SeatColor')
    seat_tier_section = xml_data['Root']['UserDataU8Map']['val']['member'] if xml_data['Root']['UserDataU8Map']['Name'] == 'SeatTier' else Exception("SeatTier not found")
    home_away_neutral_section = next(sec['val']['member'] for sec in xml_data['Root']['UserDataFloatMap'] if sec['Name'] == 'HomeAwayNeutral')
    home_away_ultra_section = next(sec['val']['member'] for sec in xml_data['Root']['UserDataFloatMap'] if sec['Name'] == 'HomeAwayUltra')
    home_away_fifty_fifty_section = next(sec['val']['member'] for sec in xml_data['Root']['UserDataFloatMap'] if sec['Name'] == 'HomeAwayFiftyFifty')
    attendance_section = next(sec['val']['member'] for sec in xml_data['Root']['UserDataFloatMap'] if sec['Name'] == 'Attendance')
    orientation_section = next(sec['val']['member'] for sec in xml_data['Root']['UserDataFloatMap'] if sec['Name'] == 'Orientation')
    
    crowd_points = []

    for i, member in enumerate(vec3_data):
        position_element = member['CrowdPlacementPointCloudData']['Position']['Vec3']
        position = Position(
            float(position_element['x']),
            float(position_element['y']),
            float(position_element['z'])
        )
    
        crowd_point = CrowdPoint(
            position,
            hex_to_rgba(card_color_section[i]['#text'][2:]),
            hex_to_rgba(seat_color_section[i]['#text'][2:]),
            int(seat_tier_section[i]['#text']),
            float(home_away_neutral_section[i]['#text']),
            float(home_away_ultra_section[i]['#text']),
            float(home_away_fifty_fifty_section[i]['#text']),
            float(attendance_section[i]['#text']),
            float(orientation_section[i]['#text'])
        )
        
        crowd_points.append(crowd_point)
        logging.debug(f"Added {i} crowd point")
    
    return CrowdData(crowd_points)


# Usage example
crowd_path =  os.path.join(main_folder, 'lens_crowd_wip.xml')

 
main_class_instance = deserialize_crowd_points(crowd_path)

for cp in main_class_instance.crowd_points:
    print(f"Position: ({cp.position.x}, {cp.position.y}, {cp.position.z})")





