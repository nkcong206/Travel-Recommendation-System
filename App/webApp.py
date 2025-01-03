import streamlit as st
from streamlit_float import *
from streamlit_folium import st_folium
import folium
import requests  # Để sử dụng API OSRM
import os
import re
import json
import query_data
import random
from datetime import datetime, timedelta
import math

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import psycopg2

# Khởi tạo `float_init`
float_init(theme=True, include_unstable_primary=False)

gemini_key = "AIzaSyBrSC3MjwkjHBqUVOULn2qShPM04BmcLls"

@st.cache_resource
def get_gemini(key):
    os.environ["GOOGLE_API_KEY"]=key
    return ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

if 'model' not in st.session_state:
    st.session_state.model = get_gemini(gemini_key)


postgres_url = "postgresql://public_owner:7CBm0fdOPkgz@ep-sweet-field-a1urmrzw.ap-southeast-1.aws.neon.tech/public?sslmode=require"



travel_type_list = ["Nghỉ dưỡng", "Khám phá"]
companion_list = ["friends", "family", "colleagues"]
transport_list = ["self-drive car", "motorbike", "bicycle", "public transport"]
city_list = ["Hà Nội"]
district_list = ["Ba Đình", "Hoàn Kiếm", "Tây Hồ", "Long Biên", "Cầu Giấy", "Đống Đa", "Hai Bà Trưng", "Hoàng Mai", "Thanh Xuân", "Nam Từ Liêm", "Bắc Từ Liêm", "Hà Đông", "Sơn Tây"]

style_list_str = [
    "Business",
    "Adventure",
    "Romantic",
    "Eco-friendly",
    "Business",
    "Wellness",
    "Family-friendly",
    "Cultural",
    "Romantic",
    "Beachfront",
    "Luxury",
    "Boutique",
    "Eco-friendly",
    "Adventure",
    "Family-friendly",
    "Boutique",
    "Cultural",
    "Wellness",
    "Luxury"
]
res_type_list_str = [ 
    "Karaoke",
    "Café/Dessert",
    "Buffet",
    "Ăn vặt/vỉa hè",
    "Tiệc cưới/Hội nghị",
    "Quán ăn",
    "Tiệm bánh",
    "Ăn chay",
    "Nhà hàng"
]
res_suit_list_str = [
    "Uống bia - Nhậu",
    "Ăn gia đình",
    "Ăn chay",
    "Ăn Fastfood",
    "Đãi tiệc",
    "Tiếp khách",
    "Takeaway - Mang về",
    "Họp nhóm",
    "Ăn vặt",
    "Nghe nhạc",
    "Du lịch",
    "Ngắm cảnh",
    "Chụp hình - Quay phim",
    "BBQ - Món Nướng",
    "Tiệc ngoài trời",
    "Thư giãn",
    "Hẹn hò",
    "Buffet"
]
att_type_list_str = [
    "Nhà hát và biểu diễn",
    "Viện bảo tàng lịch sử",
    "Thủy cung",
    "Khu vực đi dạo tham quan di tích lịch sử",
    "Trường đại học và trường học",
    "Quán bar và câu lạc bộ",
    "Khu vực đi dạo ngắm cảnh",
    "Viện bảo tàng nghệ thuật",
    "Vườn",
    "Di tích cổ",
    "Nhà thờ và nhà thờ lớn",
    "ATV và xe địa hình",
    "Đài kỷ niệm và tượng",
    "Cầu",
    "Chuyến tham quan văn hóa",
    "Xưởng vẽ và làm đồ gốm",
    "Núi",
    "Địa điểm giáo dục",
    "Khu liên hợp thể thao",
    "Buổi học và hội thảo",
    "Cửa hàng đồ cổ",
    "Sân gôn",
    "Triển lãm",
    "Đấu trường và sân vận động",
    "Phòng trưng bày nghệ thuật",
    "Điểm thu hút khách tham quan và thắng cảnh",
    "Địa điểm tâm linh"
    "Chợ hoa",
    "Cửa hàng của nhà máy",
    "Trung tâm nghệ thuật",
    "Quán bar rượu vang",
    "Căn cứ và doanh trại quân đội",
    "Địa điểm lịch sử",
    "Công viên nước",
    "Chuyến tham quan cà phê và trà",
    "Nhà hát",
    "Trung tâm trò chơi và giải trí",
    "Bảo tàng dành cho trẻ em",
    "Viện bảo tàng quân đội",
    "Bãi biển",
    "Chuyến tham quan mua sắm",
    "Địa điểm tôn giáo",
    "Trò chơi giải thoát",
    "Đường đua ô tô",
    "Chuyến tham quan tư nhân",
    "Trung tâm hành chính",
    "Sự kiện văn hóa",
    "Cửa hàng đặc sản",
    "Địa điểm tôn giáo",
    "Đài và tháp quan sát",
    "Hình thái địa chất",
    "Chợ trời",
    "Cửa hàng đồ cổ",
    "Sở thú",
    "Vùng nước",
    "Đài tháp quan sát",
    "Viện bảo tàng nghệ thuật",
    "Viện bảo tàng khoa học",
    "Địa điểm lịch sử",
    "Khu du lịch",
    "Trung tâm mua sắm",
    "Quầy bar xì gà",
    "Nông trại",
    "Công viên",
    "Lớp học nấu ăn",
    "Làng nghề truyền thống",
    "Sân chơi",
    "Tòa nhà chính phủ",
    "Rạp hát",
    "Sân golf mini",
    "Di tích cổ",
    "Viện bảo tàng chuyên ngành",
    "Chuyến tham quan cưỡi ngựa",
    "Công viên quốc gia",
    "Spa nước nóng",
    "Hệ thống giao thông công cộng",
    "Rạp hát Nhà hát và biểu diễn",
    "Lớp nấu ăn",
    "Cửa hàng bách hóa",
    "Chợ nông sản",
    "Khu phố cổ",
    "Trung tâm và trại thể thao"
]

def process_request(query):
    template = """
You are an AI travel suggestion chatbot. Analyze the following travel request:

Request: "{travel_request}"

Extract general and specific requirements for Hotels, Restaurants, and Tourist Attractions, even if some are not explicitly mentioned. For each type, provide the following information:

**General Requirements:**
- Type: From this list: {travel_type_list} based on request or return null if not specified or only ask for one of Hotels, Restaurants, or Tourist Attractions.
- Number_of_people: Extract the number of people or return null if not specified.
- Companions: Extract the companions mentioned and from this list: {companion_list} or return null if not specified.
- Transportation: Identify the transportation method mentioned and from this list: {transport_list} or return null if not specified.
- Time: Any specific dates or time ranges mentioned or return null if not specified.
- City: The mentioned city (without "city" or "province") and from this list: {city_list}.
- District: The mentioned district (without "district") and must be one frin this list: {district_list} or else return null.
- Price_range: Specify as "low", "medium", or "high" based on the request.

**For Hotels, also identify:**
- Requirements: A summary text of specific requirements or preferences mentioned.
- Style: From this list: {style_list}

**For Restaurants, also identify:**
- Requirements: A summary text of specific requirements or preferences mentioned.
- Restaurant_Type: From this list: {restaurant_type_list}
- Suitable_For: From this list: {suitable_for_list}

**For Tourist Attractions, also identify:**
- Requirements: A list of specific requirements or preferences mentioned.
- Attraction_Type: From this list: {attraction_type_list}

Return the result using the following JSON format:

```json
{{
"General": {{
    "Type": "...",
    "Number_of_people": "...",
    "Companion": "...",
    "Transportation": "...",
    "Time": "...",
    "City": "...",
    "District": "...",
    "Price_range": "...",
    "
}},
"Hotel": {{
    "Requirements": ...,
    "Style": "..."
}},
"Restaurant": {{
    "Requirements": ...,
    "Restaurant_Type": "...",
    "Suitable_For": "..."
}},
"TouristAttraction": {{
    "Attraction_Type": "..."
}}
}}

```

Ensure the JSON is valid. Use null for any unspecified information.
After the JSON output, add a note in Vietnamese:

"Nếu bạn cần thay đổi hoặc bổ sung bất kỳ thông tin nào, vui lòng cho tôi biết."
"""
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | st.session_state.model
    response = chain.invoke({
    "travel_request": query,
    "travel_type_list": travel_type_list,
    "companion_list": companion_list,
    "transport_list": transport_list,
    "city_list": city_list,
    "district_list": district_list,
    "style_list": style_list_str,
    "restaurant_type_list": res_type_list_str,
    "suitable_for_list": res_suit_list_str,
    "attraction_type_list": att_type_list_str
})

# Extract and parse the JSON response
    json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
    if json_match:
        result_dict = json.loads(json_match.group(0))
            
            # Print the JSON result
            
        return result_dict
def parse_tour_duration(duration_str):
    # Parse the duration string in 'HH:MM:SS' format
    time_parts = list(map(int, duration_str.split(':')))
    return timedelta(hours=time_parts[0], minutes=time_parts[1], seconds=time_parts[2])
    
# --- Hàm Tiện Ích ---

def haversine(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371  # Bán kính Trái Đất (km)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2.0)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2.0)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1 - a))
    meters = R * c * 1000
    return meters

# Hàm tính tổng thời gian của lộ trình
def calculate_total_time(itinerary):
    hotel = itinerary['hotel']
    places = itinerary['places']
    speed_kmh = 40
    total_time = timedelta()
    locations = []

    # Kiểm tra hotel['location'] trước khi thêm vào danh sách locations
    if hotel.get('location') and hotel['location'].get('coordinates'):
        locations.append(hotel['location']['coordinates'])

    # Kiểm tra từng địa điểm (place) và thêm vào locations nếu có thông tin hợp lệ
    for place in places:
        if place.get('location') and place['location'].get('coordinates'):
            locations.append(place['location']['coordinates'])

    # Đảm bảo rằng locations không bị rỗng hoặc có giá trị None
    if not locations:
        st.write("Không có tọa độ hợp lệ để tính toán lộ trình.")
    else:
        # Tiến hành các bước tiếp theo, ví dụ: vẽ bản đồ, tính toán thời gian, v.v.
        pass

    for i in range(len(locations) - 1):
        # Kiểm tra tọa độ hợp lệ trước khi tính toán
        lat1, lon1 = locations[i]
        lat2, lon2 = locations[i + 1]

        if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
            # Thời gian di chuyển
            distance_meters = haversine([lat1, lon1], [lat2, lon2])
            distance_km = distance_meters  # Khoảng cách tính bằng km
            travel_time_hours = distance_km / speed_kmh  # Tính thời gian di chuyển
            travel_time = timedelta(hours=travel_time_hours)
            total_time += travel_time

            # Thời gian ở địa điểm
            place = places[i]
            if 'tour_duration' in place:
                # Nếu có thời gian du lịch tại địa điểm, cộng vào tổng thời gian
                total_time += parse_tour_duration(place['tour_duration'])
            else:
                # Nếu không có, giả sử là 1 giờ
                total_time += timedelta(hours=1)

        else:
            st.write(f"**Lỗi tọa độ không hợp lệ tại địa điểm {places[i]['name']} và {places[i+1]['name']}:**")
            st.write(f"  {lat1}, {lon1} và {lat2}, {lon2}")

    return total_time

# --- Hàm Tính Fitness ---
def parse_location(location):
    if isinstance(location, dict):
        return float(location.get('lat', 0)), float(location.get('lon', 0))
    elif isinstance(location, str):
        try:
            lat, lon = map(float, location.split(','))
            return lat, lon
        except ValueError:
            raise ValueError(f"Invalid location string: {location}")
    elif isinstance(location, (list, tuple)) and len(location) == 2:
        return float(location[0]), float(location[1])
    else:
        raise ValueError(f"Unexpected location format: {location}")

def compute_itinerary_fitness_experience(itinerary):
    hotel = itinerary['hotel']
    places = itinerary['places']

    # Helper function to parse locations

    # Parse places locations
    try:
        places_locations = [parse_location(place['location']) for place in places]
    except ValueError as e:
        print("Error parsing a place location:", e)
        return None

    # Calculate places score
    total_places_rating = sum(place.get('rating', 0) for place in places) * 20
    places_score = total_places_rating + len(places) * 40

    # Tính tổng khoảng cách di chuyển
    total_distance = 0
    locations = []

    # Check if hotel has location and coordinates
    if hotel.get('location') and hotel['location'].get('coordinates'):
        locations.append(hotel['location']['coordinates'])
    else:
        locations.append(None)  # Add None if hotel location is missing

    # Add places' locations if they exist
    for place in places_locations:
        if place.get('location') and place['location'].get('coordinates'):
            locations.append(place['location']['coordinates'])
        else:
            locations.append(None)  # Add None if place location is missing

    # Filter out None values from locations list
    locations = [loc for loc in locations if loc is not None]

    # If there are no valid locations, return 0 fitness (or handle accordingly)
    if not locations:
        return 0  # or some other default value if no valid locations are found

    # Calculate the total distance for valid locations
    for i in range(len(locations) - 1):
        distance_meters = haversine(locations[i], locations[i + 1])
        total_distance += distance_meters / 1000  # Convert to kilometers

    distance_penalty = total_distance * 50  # Ưu tiên sau thời gian
    # Calculate time penalty
    total_time = calculate_total_time(itinerary)
    total_hours = total_time.total_seconds() / 3600
    time_penalty = (total_hours - 14) * 20 if total_hours > 14 else 0

    # Calculate average prices
    hotel_avg_price = (
        sum(hotel['price'].values()) / len(hotel['price'].values())
        if 'price' in hotel and hotel['price']
        else 0
    )

    attraction_avg_price = sum(
        sum(place.get('price', {}).values()) / len(place['price'].values())
        if 'price' in place and place['price']
        else 0
        for place in places
    )

    restaurant_avg_price = sum(
        place.get('average_price_per_person', 0) for place in places
    )

    total_price = hotel_avg_price + attraction_avg_price + restaurant_avg_price - distance_penalty
    price_penalty = total_price * 0.1  # Moderate importance to pricing

    # Compute final fitness score
    fitness = (
        places_score
        - time_penalty
        - price_penalty
        + hotel.get('rating', 0) * 5
        - distance_penalty
    )
    return fitness


# --- Hàm Tạo Quần Thể Ban Đầu ---

def generate_initial_population_experience(hotels, tourist_attractions, restaurants, pop_size, user_requirements):
    population = []
    # Lọc điểm tham quan theo yêu cầu
    filtered_attractions = [
    attr for attr in tourist_attractions
    if any(attraction in user_requirements.get('TouristAttraction', {}).get('Attraction_Type', [])
           for attraction in attr.get('attraction_type', []))
    ]
    if not filtered_attractions:
        filtered_attractions = tourist_attractions

    # Lọc nhà hàng theo yêu cầu
    filtered_restaurants = [res for res in restaurants if
                            set(user_requirements.get('Restaurant',{}).get('Suitable_For', [])).intersection(res.get('suitable_for', []))]
    if not filtered_restaurants:
        filtered_restaurants = restaurants

    for _ in range(pop_size):
        itinerary = {}
        # Chọn khách sạn ngẫu nhiên
        itinerary['hotel'] = random.choice(hotels)
        # Chọn nhiều điểm tham quan
        num_places = random.randint(5, 8)
        all_places = filtered_attractions + filtered_restaurants
        if len(all_places) >= num_places:
            itinerary['places'] = random.sample(all_places, num_places)
        else:
            itinerary['places'] = all_places
        population.append(itinerary)
    return population

# --- Hàm Lai Ghép và Đột Biến (giữ nguyên từ phần trước) ---

def crossover_itineraries(parent1, parent2):
    child = {}
    child['hotel'] = random.choice([parent1['hotel'], parent2['hotel']])
    places1 = parent1['places']
    places2 = parent2['places']
    min_len = min(len(places1), len(places2))

    if min_len > 1:
        cut_point = random.randint(1, min_len - 1)
        child_places = places1[:cut_point] + places2[cut_point:]
    else:
        child_places = places1 + places2

    # Loại bỏ trùng lặp
    seen = set()
    unique_places = []
    for place in child_places:
        if place['name'] not in seen:
            unique_places.append(place)
            seen.add(place['name'])
    child['places'] = unique_places
    return child

def mutate_itinerary(hotels, tourist_attractions, restaurants,itinerary):
    if random.random() < 0.1:
        if len(itinerary['places']) > 0:
            index = random.randint(0, len(itinerary['places'])-1)
            new_place = random.choice(tourist_attractions + restaurants)
            itinerary['places'][index] = new_place
    if random.random() < 0.05:
        itinerary['hotel'] = random.choice(hotels)

def genetic_algorithm_experience(hotels, tourist_attractions, restaurants, generations=50, population_size=20, user_requirements=None):
    if user_requirements is None:
        user_requirements = {}
    population = generate_initial_population_experience(hotels, tourist_attractions, restaurants, population_size, user_requirements)

    for generation in range(generations):
        fitness_scores = []
        for itinerary in population:
            fitness = compute_itinerary_fitness_experience(itinerary)
            fitness_scores.append((fitness, itinerary))
        fitness_scores.sort(reverse=True, key=lambda x: x[0])
        population = [it for (fit, it) in fitness_scores]

        num_selected = population_size // 2
        selected = population[:num_selected]
        offspring = []
        while len(offspring) < population_size - num_selected:
            parent1 = random.choice(selected)
            parent2 = random.choice(selected)
            child = crossover_itineraries(parent1, parent2)
            mutate_itinerary(hotels, tourist_attractions, restaurants,child)
            offspring.append(child)
        population = selected + offspring

    best_itinerary = population[0]
    best_fitness = compute_itinerary_fitness_experience(best_itinerary)
    return best_itinerary, best_fitness

# Hàm xử lý nội dung chat
def chat_content():
    # Lưu tin nhắn người dùng vào session_state
    user_input = st.session_state.content
    # Thêm tin nhắn của người dùng vào list trong session_state
    st.session_state['contents'].append({"role": "user", "content": user_input})
    response = process_request(user_input)
    st.session_state['response'] = response
    print(response)
    general_requirements = response.get("General", {})
    hotel_requirements = response.get("Hotel", {})
    restaurant_requirements = response.get("Restaurant", {})
    attraction_requirements = response.get("TouristAttraction", {})
    
    hotel_query_indi = query_data.build_sql_query_individual("hotel", hotel_requirements, general_requirements)

    restaurant_query_indi = query_data.build_sql_query_individual("restaurant", restaurant_requirements, general_requirements)

    attraction_query_indi = query_data.build_sql_query_individual("touristattraction", attraction_requirements, general_requirements)

    hotel_locations = query_data.fetch_locations(hotel_query_indi, postgres_url)
    restaurant_locations = query_data.fetch_locations(restaurant_query_indi, postgres_url)
    attraction_locations = query_data.fetch_locations(attraction_query_indi, postgres_url)
    #travel_type = response.get('General',{}).get('Type', None)

    best_itinerary_relaxation, best_fitness_relaxation = genetic_algorithm_experience(user_requirements = response, hotels = hotel_locations, tourist_attractions = attraction_locations, restaurants = restaurant_locations)

    st.session_state['locations'] = best_itinerary_relaxation
    print(best_itinerary_relaxation)
    bot_response = st.session_state['response']
    # Thêm phản hồi của bot vào list trong session_state
    st.session_state['contents'].append({"role": "assistant", "content": bot_response})

# Khởi tạo `contents` và `locations` nếu chưa có
if 'contents' not in st.session_state:
    st.session_state['contents'] = []
if 'locations' not in st.session_state:
    st.session_state['locations'] = False  # Khởi tạo với lộ trình trống

border = False

# Chia bố cục thành 2 cột chiếm hết chiều ngang màn hình
col1, col2 = st.columns([1, 1])  # Tỷ lệ 1:1, bạn có thể thay đổi tỷ lệ này tùy ý


# Cột bên trái: Giao diện chat
with col1:
    with st.container(border=border):
        with st.container():
            # Ô nhập chat cố định
            st.chat_input("Nhập yêu cầu của bạn...", key='content', on_submit=chat_content) 
            button_b_pos = "0rem"
            button_css = float_css_helper(width="2.2rem", bottom=button_b_pos, transition=0)
            float_parent(css=button_css)

        # Hiển thị lịch sử hội thoại với icon của bot và người dùng
        for c in st.session_state.contents:
            if isinstance(c, dict):  # Kiểm tra chắc chắn rằng `c` là một từ điển
                # Hiển thị tin nhắn của người dùng
                if c.get("role") == "user":
                    with st.chat_message(name="user"):
                        st.write(c.get("content", ""))
            
                # Hiển thị phản hồi của bot với icon
                elif c.get("role") == "assistant":
                    with st.chat_message(name="assistant"):
                        st.write(c.get("content", ""))

# Cập nhật hàm in lộ trình để hiển thị thông tin lộ trình và vẽ đường đi
# Cập nhật hàm in lộ trình để hiển thị thông tin lộ trình và vẽ đường đi
def print_itinerary_experience(itinerary):
    hotel = itinerary['hotel']
    if isinstance(hotel['price'], dict):
        hotel_avg_price = sum(hotel['price'].values()) / len(hotel['price'].values())
    else:
        hotel_avg_price = hotel['price']
    
    # Danh sách tọa độ (đã đảo ngược tọa độ)
    locations = []
    
    # Kiểm tra nếu khách sạn có tọa độ hợp lệ
    if hotel.get('location') and hotel['location'].get('coordinates'):
        locations.append(hotel['location']['coordinates'])
    
    # Kiểm tra nếu các địa điểm trong lộ trình có tọa độ hợp lệ
    for place in itinerary.get('places', []):
        if place.get('location') and place['location'].get('coordinates'):
            locations.append(place['location']['coordinates'])
    
    total_time = timedelta()
    total_distance = 0
    total_price = hotel_avg_price

    # Khởi tạo bản đồ với vị trí trung tâm là khách sạn
    if hotel.get('location') and hotel['location'].get('coordinates'):
        map_center = [hotel['location']['coordinates'][1], hotel['location']['coordinates'][0]]  # Đảo ngược tọa độ
    else:
        map_center = [0, 0]  # Vị trí mặc định nếu không có tọa độ hợp lệ
    map_object = folium.Map(location=map_center, zoom_start=14)
    
    # Thêm khách sạn vào bản đồ
    if hotel.get('location') and hotel['location'].get('coordinates'):
        folium.Marker(
            location=[hotel['location']['coordinates'][1], hotel['location']['coordinates'][0]],  # Đảo ngược tọa độ
            popup=f"Khách sạn: {hotel['name']}",
            icon=folium.Icon(color='blue')  # Màu xanh dương cho khách sạn
        ).add_to(map_object)

    # Khởi tạo màu sắc cho các đoạn đường
    route_colors = ["blue", "green", "red", "purple", "orange", "pink", "brown", "gray", "lightblue"]

    for i, place in enumerate(itinerary['places']):
        if i < len(locations) - 1:  # Đảm bảo không vượt quá chỉ số
            lat1, lon1 = locations[i]
            lat2, lon2 = locations[i+1] if i+1 < len(locations) else (None, None)

            # Tính thời gian di chuyển và khoảng cách giữa khách sạn và các địa điểm
            if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
                distance_meters = haversine([lat1, lon1], [lat2, lon2])
                distance_km = distance_meters / 1000
                total_distance += distance_km
                travel_time_hours = distance_km / 40  # Tốc độ 40 km/h
                travel_time = timedelta(hours=travel_time_hours)
                travel_time_minutes = int(travel_time.total_seconds() / 60)

                # Thời gian ở địa điểm
                if 'tour_duration' in place:
                    duration = parse_tour_duration(place['tour_duration'])
                else:
                    duration = timedelta(hours=1)

                total_time += travel_time + duration

                # Tính giá
                if 'price' in place and isinstance(place['price'], dict):
                    price = sum(place['price'].values()) / len(place['price'].values())
                else:
                    price = place.get('average_price_per_person', 0)
                
                total_price += price

                # Thêm marker cho địa điểm
                if place.get('location') and place['location'].get('coordinates'):
                    folium.Marker(
                        location=[place['location']['coordinates'][1], place['location']['coordinates'][0]],  # Đảo ngược tọa độ
                        popup=f"{place['name']} - {place['description']}",
                        icon=folium.Icon(color='red')  # Màu đỏ cho các địa điểm khác
                    ).add_to(map_object)
    
    # Vẽ đường đi giữa các điểm trong lộ trình (bao gồm khách sạn)
    for i in range(len(locations) - 1):
        lat_A = locations[i][1]
        lon_A = locations[i][0]
        lat_B = locations[i+1][1]
        lon_B = locations[i+1][0]

        # Gọi API OSRM để tính toán đường đi
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{lon_A},{lat_A};{lon_B},{lat_B}?overview=full&geometries=geojson"
        response = requests.get(osrm_url)
        data = response.json()

        if 'routes' in data:
            route = data['routes'][0]['geometry']['coordinates']
            route_latlon = [[coord[1], coord[0]] for coord in route]  # Đảo ngược tọa độ

            # Tính màu nhạt dần và độ mờ
            color_intensity = 255 - int((i / (len(locations) - 1)) * 255)
            color_hex = f"#{color_intensity:02x}{color_intensity:02x}ff"  # Từ xanh dương chuyển dần sang trắng
            opacity = 0.8 - (i / (len(locations) - 1)) * 0.5  # Độ mờ giảm dần từ 0.8 đến 0.3

            # Thêm đường đi vào bản đồ với màu sắc và độ nhạt dần
            folium.PolyLine(route_latlon, color=color_hex, weight=5, opacity=opacity).add_to(map_object)

    # Hiển thị bản đồ
    st_data = st_folium(map_object, width=700, height=500)
    # Sử dụng st.write để thay thế print
    st.write("\n**Lộ trình Khám Phá Tối Ưu:**")
    st.write(f"**Khách sạn:** {hotel['name']} - Đánh giá: {hotel['rating']}")
    st.write(f"**Giá mỗi đêm:** VND{hotel_avg_price}")
    for i, place in enumerate(itinerary['places']):
        lat1, lon1 = locations[i]
        lat2, lon2 = locations[i+1] if i+1 < len(locations) else (None, None)

        # Tính thời gian di chuyển và khoảng cách giữa khách sạn và các địa điểm
        if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
            distance_meters = haversine([lat1, lon1], [lat2, lon2])
            distance_km = distance_meters / 1000
            total_distance += distance_km
            travel_time_hours = distance_km / 40  # Tốc độ 40 km/h
            travel_time = timedelta(hours=travel_time_hours)
            travel_time_minutes = int(travel_time.total_seconds() / 60)

            # Thời gian ở địa điểm
            if 'tour_duration' in place:
                duration = parse_tour_duration(place['tour_duration'])
            else:
                duration = timedelta(hours=1)

            total_time += travel_time + duration

            # Tính giá
            if 'price' in place and isinstance(place['price'], dict):
                price = sum(place['price'].values()) / len(place['price'].values())
            else:
                price = place.get('average_price_per_person', 0)
            
            total_price += price

            # In thông tin địa điểm
            st.write(f"\n**Di chuyển đến {place['name']}:**")
            st.write(f"  Khoảng cách: {distance_km:.2f} km")
            st.write(f"  Thời gian di chuyển: {travel_time_minutes} phút")
            st.write(f"Tại {place['name']}:")
            st.write(f"  Loại hình: {place.get('attraction_type', 'Nhà hàng')}")
            st.write(f"  Đánh giá: {place['rating']}")
            st.write(f"  Giá: VND{price}")
            if 'tour_duration' in place:
                duration_hours = int(duration.total_seconds() / 3600)
                duration_minutes = int((duration.total_seconds() % 3600) / 60)
                st.write(f"  Thời gian ở lại: {duration_hours} giờ {duration_minutes} phút")
            else:
                st.write("  Thời gian ở lại: 1 giờ")
            st.write(f"  Vị trí: {place['location']['coordinates']}")

    total_hours = total_time.total_seconds() / 3600
    st.write(f"\n**Tổng thời gian (bao gồm di chuyển):** {total_hours:.2f} giờ")
    st.write(f"**Tổng khoảng cách di chuyển:** {total_distance:.2f} km")
    st.write(f"**Tổng chi phí:** VND{total_price:.2f}")



# Cột bên phải: Bản đồ và danh sách địa điểm
with col2:
    with st.container(border=True):
        st.header("Bản đồ & Danh sách địa điểm")

        # Kiểm tra và hiển thị lộ trình
        if 'locations' in st.session_state and st.session_state['locations']:
            print_itinerary_experience(st.session_state['locations'])
        else:
            # Nếu không có lộ trình, vẽ bản đồ với tọa độ mặc định
            default_map_center = [21.0480867,105.7986559]  # Tọa độ mặc định
            default_map_object = folium.Map(location=default_map_center, zoom_start=14)
            st_data = st_folium(default_map_object, width=700, height=500)



# --- Chạy Thuật Toán và In Lộ Trình ---

# Chạy thuật toán và in lộ trình
# best_itinerary_relaxation, best_fitness_relaxation = genetic_algorithm_relaxation(
#     user_requirements=update_requires_respond
# )
# print_itinerary_relaxation(best_itinerary_relaxation)




