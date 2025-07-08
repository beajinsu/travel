# travel_map_generator.py

import os
import json
from datetime import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import folium
from folium.plugins import HeatMap

# Step 1: Google Photos API 인증
SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]
flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
creds = flow.run_local_server(port=0)
service = build("photoslibrary", "v1", credentials=creds)

# Step 2: 위치 정보 추출
coords = []
next_page_token = ""
while True:
    resp = service.mediaItems().list(pageSize=100, pageToken=next_page_token).execute()
    for item in resp.get("mediaItems", []):
        loc = item.get("mediaMetadata", {}).get("location")
        if loc:
            coords.append({
                "lat": float(loc["latitude"]),
                "lng": float(loc["longitude"]),
                "timestamp": item["mediaMetadata"].get("creationTime", "")
            })
    next_page_token = resp.get("nextPageToken")
    if not next_page_token:
        break

# Step 3: 지도 생성
if not coords:
    raise ValueError("위치 정보를 가진 사진이 없습니다.")

first = coords[0]
map_ = folium.Map(location=[first["lat"], first["lng"]], zoom_start=5)

# HeatMap 레이어 추가
heat_data = [[c["lat"], c["lng"]] for c in coords]
HeatMap(heat_data).add_to(map_)

# 예시: 수동 마커 추가 (나중에 외부 링크와 함께 확장 가능)
custom_places = [
    {
        "lat": 35.6895,
        "lng": 139.6917,
        "name": "도쿄",
        "link": "https://polarsteps.com/yourtrip_tokyo"
    },
    {
        "lat": 48.8566,
        "lng": 2.3522,
        "name": "파리",
        "link": "https://journey.app/shared/paris-trip"
    }
]

for place in custom_places:
    folium.Marker(
        location=[place["lat"], place["lng"]],
        popup=folium.Popup(f'<a href="{place["link"]}" target="_blank">{place["name"]} 여행기 보기</a>', max_width=300),
        tooltip=place["name"]
    ).add_to(map_)

# Step 4: 저장
map_.save("my_travel_map.html")
print("✅ 지도 생성 완료: my_travel_map.html")

