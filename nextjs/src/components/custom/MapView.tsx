"use client";

import Map, { Marker, MapRef } from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";
import { Building } from "@/types";
import { useEffect, useRef, useState } from "react";
import { LngLatBounds } from "maplibre-gl";

type Props = {
  buildings: Building[];
  onSelect: (building: Building) => void;
  onAdd: (lat: number, lng: number) => void;
};

export default function MapView({ buildings, onSelect, onAdd }: Props) {
  const mapRef = useRef<MapRef | null>(null);
  const [userLocation, setUserLocation] = useState<{
    lat: number;
    lng: number;
  } | null>(null);
  const [addLocation, setAddLocation] = useState<{
    lat: number;
    lng: number;
  } | null>(null);

  useEffect(() => {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setUserLocation({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
        });
      },
      (err) => {
        console.warn("사용자 위치를 가져올 수 없습니다:", err);
      },
      { enableHighAccuracy: true }
    );
  }, []);

  const handleMapLoad = () => {
    const map = mapRef.current;
    if (!map) return;

    const bounds = new LngLatBounds();
    if (userLocation) bounds.extend([userLocation.lng, userLocation.lat]);
    for (const b of buildings) bounds.extend([b.longitude, b.latitude]);
    if (!bounds.isEmpty()) {
      map.fitBounds(bounds, { padding: 50, duration: 1000, maxZoom: 15 });
    }
  };

  return (
    <Map
      ref={mapRef}
      onLoad={handleMapLoad}
      mapLib={import("maplibre-gl")}
      initialViewState={{
        latitude: userLocation?.lat ?? 37.5665,
        longitude: userLocation?.lng ?? 126.978,
        zoom: 16,
      }}
      onClick={(e) => {
        const { lat, lng } = e.lngLat;
        setAddLocation({ lat, lng });
      }}
      style={{ width: "100%", height: "100%" }}
      mapStyle="https://tiles.stadiamaps.com/styles/osm_bright.json"
    >
      {userLocation && (
        <Marker
          latitude={userLocation.lat}
          longitude={userLocation.lng}
          color="blue"
        />
      )}

      {buildings.map((b) => (
        <Marker
          key={b.building_id}
          latitude={b.latitude}
          longitude={b.longitude}
          onClick={() => onSelect(b)}
        />
      ))}

      {addLocation && (
        <Marker
          latitude={addLocation.lat}
          longitude={addLocation.lng}
          color="red"
          onClick={() => {
            onAdd(addLocation.lat, addLocation.lng);
            setAddLocation(null);
          }}
        />
      )}
    </Map>
  );
}
