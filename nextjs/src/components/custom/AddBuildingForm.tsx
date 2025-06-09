"use client";

import { useState } from "react";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { useAddBuilding } from "@/hooks/building";

type AddBuildingFormProps = {
  lat: number;
  lng: number;
  onDone: () => void;
};

export function AddBuildingForm({ lat, lng, onDone }: AddBuildingFormProps) {
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const { mutateAsync: addBuilding, isPending } = useAddBuilding();

  const handleSubmit = async () => {
    setError("");
    try {
      const result = await addBuilding({ name, latitude: lat, longitude: lng });
      if (!result.success) {
        setError(result.message);
        return;
      }
      onDone();
    } catch (err) {
      console.error(err);
      setError("서버 오류가 발생했습니다.");
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">건물 추가</h2>
      <Input
        placeholder="건물 이름"
        value={name}
        onChange={(e) => setName(e.target.value)}
        disabled={isPending}
      />
      <div className="text-sm text-gray-600">
        위도: {lat.toFixed(6)}, 경도: {lng.toFixed(6)}
      </div>
      {error && <div className="text-sm text-red-500">{error}</div>}
      <Button
        onClick={handleSubmit}
        disabled={isPending || !name}
        variantIntent="primary"
      >
        {isPending ? "추가 중..." : "추가"}
      </Button>
    </div>
  );
}
