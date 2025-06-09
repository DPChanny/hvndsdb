"use client";

export const dynamic = "force-dynamic";

import nextDynamic from "next/dynamic";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { useEffect, useRef, useState, useCallback } from "react";
import { useBuildingList } from "@/hooks/building";
import { Building } from "@/types";
import { Modal } from "@/components/ui/Modal";
import { AddBuildingForm } from "@/components/custom/AddBuildingForm";
import { AnalyzerPanel } from "@/components/custom/AnalyzerPanel";
import { BuildingPanel } from "@/components/custom/BuildingPanel";
import { ViewerPanel } from "@/components/custom/ViewerPanel";

const MapView = nextDynamic(() => import("@/components/custom/MapView"), {
  ssr: false,
});

export default function BuildingMapPage() {
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();

  const { data, isLoading } = useBuildingList();
  const buildingId = params.get("buildingId");
  const modalType = params.get("modal");

  const [selectedBuilding, setSelectedBuilding] = useState<Building | null>(
    null
  );
  const [addLatLng, setAddLatLng] = useState<{
    lat: number;
    lng: number;
  } | null>(null);

  useEffect(() => {
    if (!buildingId || !data?.data) return;
    const building =
      data.data.find((b) => b.building_id === buildingId) ?? null;
    setSelectedBuilding(building);
  }, [buildingId, data]);

  const buildings: Building[] = data?.data ?? [];

  const viewerWebSocket = useRef<WebSocket | null>(null);
  const [isViewerConnected, setIsViewerConnected] = useState(false);
  useEffect(() => {
    viewerWebSocket.current = new WebSocket(
      `ws://${process.env.NEXT_PUBLIC_FASTAPI_HOST}:${process.env.NEXT_PUBLIC_FASTAPI_PORT}/ws/viewer`
    );
    viewerWebSocket.current.onopen = () => setIsViewerConnected(true);
    viewerWebSocket.current.onclose = () => setIsViewerConnected(false);
    return () => viewerWebSocket.current?.close();
  }, []);

  const analyzerWebSocket = useRef<WebSocket | null>(null);
  const [isAnalyzerConnected, setIsAnalyzerConnected] = useState(false);
  useEffect(() => {
    analyzerWebSocket.current = new WebSocket(
      `ws://${process.env.NEXT_PUBLIC_FASTAPI_HOST}:${process.env.NEXT_PUBLIC_FASTAPI_PORT}/ws/analyzer`
    );
    analyzerWebSocket.current.onopen = () => setIsAnalyzerConnected(true);
    analyzerWebSocket.current.onclose = () => setIsAnalyzerConnected(false);
    return () => analyzerWebSocket.current?.close();
  }, []);

  const closeModal = useCallback(() => {
    router.replace(pathname);
    setAddLatLng(null);
  }, [router, pathname]);

  const handleAdd = useCallback(
    (lat: number, lng: number) => {
      if (!addLatLng) {
        setAddLatLng({ lat, lng });
        router.push(`${pathname}?modal=add`);
      }
    },
    [router, pathname, addLatLng]
  );

  const handleAddDone = useCallback(() => {
    closeModal();
    setAddLatLng(null);
  }, [closeModal]);

  return (
    <div className="w-full h-screen relative">
      {isLoading ? (
        <p>Loading...</p>
      ) : buildings.length === 0 ? (
        <div className="flex items-center justify-center h-full text-sm text-gray-500">
          등록된 건물이 없습니다.
        </div>
      ) : (
        <MapView
          buildings={buildings}
          onSelect={(b) =>
            router.push(`${pathname}?modal=detail&buildingId=${b.building_id}`)
          }
          onAdd={handleAdd}
        />
      )}

      {modalType === "detail" && selectedBuilding && (
        <Modal open onClose={closeModal}>
          <h2 className="text-lg font-bold">{selectedBuilding.name}</h2>
          <BuildingPanel buildingId={selectedBuilding.building_id} />
        </Modal>
      )}

      {modalType === "add" && addLatLng && (
        <Modal open onClose={closeModal}>
          <AddBuildingForm
            lat={addLatLng.lat}
            lng={addLatLng.lng}
            onDone={handleAddDone}
          />
        </Modal>
      )}

      {modalType === "analyze" && buildingId && selectedBuilding && (
        <Modal open onClose={closeModal}>
          <h2 className="text-lg font-bold">{selectedBuilding.name}</h2>
          <AnalyzerPanel
            ws={analyzerWebSocket.current}
            isConnected={isAnalyzerConnected}
            buildingId={buildingId}
            onClose={closeModal}
          />
        </Modal>
      )}

      {modalType === "viewer" && buildingId && selectedBuilding && (
        <Modal open onClose={closeModal}>
          <h2 className="text-lg font-bold">{selectedBuilding.name}</h2>
          <ViewerPanel
            ws={viewerWebSocket.current}
            isConnected={isViewerConnected}
            buildingId={buildingId}
            onClose={closeModal}
          />
        </Modal>
      )}
    </div>
  );
}
