from lxml import etree

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
        self.crowd_points = crowd_points

def find_parent_by_child_value(root, element_type, child_tag, child_value):
    for element in root.findall(f'.//{element_type}'):
        child = element.find(child_tag)
        if child is not None and child.text == child_value:
            return element
    return None

def parse_user_data(element, count):
    values = []
    for i in range(count):
        member = element.find(f'val/member[{i+1}]')
        values.append(member.text if member is not None else None)
    return values

def deserialize_crowd_points(xml_file_path):
    with open(xml_file_path, 'r') as file:
        xml_content = file.read()
    
    wrapped_xml_content = f"<Root>{xml_content}</Root>"
    root = etree.fromstring(wrapped_xml_content)
    
    data_section = root.find('.//CrowdPlacementPointCloudDataAsset/Data')
    crowd_point_data_elements = data_section.findall('member')

    count = len(crowd_point_data_elements)
    
    user_data_elements = {
        "CardColor": parse_user_data(find_parent_by_child_value(root, 'UserDataUintMap', 'Name', 'CardColor'), count),
        "SeatColor": parse_user_data(find_parent_by_child_value(root, 'UserDataUintMap', 'Name', 'SeatColor'), count),
        "SeatTier": parse_user_data(find_parent_by_child_value(root, 'UserDataU8Map', 'Name', 'SeatTier'), count),
        "HomeAwayNeutral": parse_user_data(find_parent_by_child_value(root, 'UserDataFloatMap', 'Name', 'HomeAwayNeutral'), count),
        "HomeAwayUltra": parse_user_data(find_parent_by_child_value(root, 'UserDataFloatMap', 'Name', 'HomeAwayUltra'), count),
        "HomeAwayFiftyFifty": parse_user_data(find_parent_by_child_value(root, 'UserDataFloatMap', 'Name', 'HomeAwayFiftyFifty'), count),
        "Attendance": parse_user_data(find_parent_by_child_value(root, 'UserDataFloatMap', 'Name', 'Attendance'), count),
        "Orientation": parse_user_data(find_parent_by_child_value(root, 'UserDataFloatMap', 'Name', 'Orientation'), count)
    }
    
    crowd_points = []
    
    for i, member in enumerate(crowd_point_data_elements):
        print(f"parse pos {i}")
        position_element = member.find('.//Vec3')
        position = Position(
            float(position_element.find('x').text),
            float(position_element.find('y').text),
            float(position_element.find('z').text)
        )

        crowd_point = CrowdPoint(
            position,
            int(user_data_elements["CardColor"][i], 16) if user_data_elements["CardColor"][i] else 0,
            int(user_data_elements["SeatColor"][i], 16) if user_data_elements["SeatColor"][i] else 0,
            int(user_data_elements["SeatTier"][i]) if user_data_elements["SeatTier"][i] else 0,
            float(user_data_elements["HomeAwayNeutral"][i]) if user_data_elements["HomeAwayNeutral"][i] else 0,
            float(user_data_elements["HomeAwayUltra"][i]) if user_data_elements["HomeAwayUltra"][i] else 0,
            float(user_data_elements["HomeAwayFiftyFifty"][i]) if user_data_elements["HomeAwayFiftyFifty"][i] else 0,
            float(user_data_elements["Attendance"][i]) if user_data_elements["Attendance"][i] else 0,
            float(user_data_elements["Orientation"][i]) if user_data_elements["Orientation"][i] else 0
        )
        
        crowd_points.append(crowd_point)

        logging.debug(f"Added {i} crowd point")
    
    return CrowdData(crowd_points)

# Usage example
main_class_instance = deserialize_crowd_points('crowd_points.xml')
for cp in main_class_instance.crowd_points:
    print(f"Position: ({cp.position.x}, {cp.position.y}, {cp.position.z})")
