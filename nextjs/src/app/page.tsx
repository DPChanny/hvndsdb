"use client";

import dynamic from "next/dynamic";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { useBuildingList } from "@/hooks/building";
import { Building } from "@/types";
import { Modal } from "@/components/ui/Modal";
import { AddBuildingForm } from "@/components/custom/AddBuildingForm";
import { AnalyzerPanel } from "@/components/custom/AnalyzerPanel";
import { BuildingPanel } from "@/components/custom/BuildingPanel";
import { Plus } from "lucide-react";

const MapView = dynamic(() => import("@/components/custom/MapView"), {
  ssr: false,
});

export default function BuildingMapPage() {
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();

  const { data, isLoading } = useBuildingList();
  const buildingId = params.get("buildingId");
  const modalType = params.get("modal"); // "detail", "add", "analyze"

  const [selectedBuilding, setSelectedBuilding] = useState<Building | null>(
    null
  );

  useEffect(() => {
    if (!buildingId || !data?.data) return;
    const building =
      data.data.find((b) => b.building_id === buildingId) ?? null;
    setSelectedBuilding(building);
  }, [buildingId, data]);

  const buildings: Building[] = data?.data ?? [];

  // WebSocket
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  useEffect(() => {
    ws.current = new WebSocket("ws://127.0.0.1:8000/ws/analyzer");
    ws.current.onopen = () => setIsConnected(true);
    ws.current.onclose = () => setIsConnected(false);
    return () => ws.current?.close();
  }, []);

  const closeModal = () => router.replace(pathname);

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
        />
      )}

      <button
        onClick={() => router.push(`${pathname}?modal=add`)}
        className="absolute bottom-12 right-12 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700"
      >
        <Plus />
      </button>

      {modalType === "detail" && selectedBuilding && (
        <Modal open onClose={closeModal}>
          <h2 className="text-lg font-bold">{selectedBuilding.name}</h2>
          <BuildingPanel buildingId={selectedBuilding.building_id} />
        </Modal>
      )}

      {modalType === "add" && (
        <Modal open onClose={closeModal}>
          <AddBuildingForm onDone={closeModal} />
        </Modal>
      )}

      {modalType === "analyze" && buildingId && selectedBuilding && (
        <Modal open onClose={closeModal}>
          <h2 className="text-lg font-bold">{selectedBuilding.name}</h2>
          <AnalyzerPanel
            ws={ws.current}
            isConnected={isConnected}
            buildingId={buildingId}
            onClose={closeModal}
          />
        </Modal>
      )}
    </div>
  );
}
