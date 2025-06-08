"use client";

import Map, { Marker, MapRef } from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";
import { Building } from "@/types";
import { useRef } from "react";
import { LngLatBounds } from "maplibre-gl";

type Props = {
  buildings: Building[];
  onSelect: (building: Building) => void;
};

export default function MapView({ buildings, onSelect }: Props) {
  const mapRef = useRef<MapRef | null>(null);

  const handleMapLoad = () => {
    const map = mapRef.current;
    if (!map || buildings.length === 0) return;

    const bounds = new LngLatBounds();
    for (const b of buildings) {
      bounds.extend([b.longitude, b.latitude]);
    }

    map.fitBounds(bounds, {
      padding: 50,
      duration: 1000,
      maxZoom: 15,
    });
  };

  return (
    <Map
      ref={mapRef}
      onLoad={handleMapLoad}
      mapLib={import("maplibre-gl")}
      initialViewState={{
        latitude: 37.5665,
        longitude: 126.978,
        zoom: 16,
      }}
      style={{ width: "100%", height: "100%" }}
      mapStyle="https://tiles.stadiamaps.com/styles/osm_bright.json"
    >
      {buildings.map((b) => (
        <Marker
          key={b.building_id}
          latitude={b.latitude}
          longitude={b.longitude}
          onClick={() => onSelect(b)}
        />
      ))}
    </Map>
  );
}
