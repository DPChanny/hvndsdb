"use client";

import { useState } from "react";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { useAddBuilding } from "@/hooks/building";

type AddBuildingFormProps = {
  onDone: () => void;
};

export function AddBuildingForm({ onDone }: AddBuildingFormProps) {
  const [name, setName] = useState("");
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [error, setError] = useState("");

  const { mutateAsync: addBuilding, isPending } = useAddBuilding();

  const handleSubmit = async () => {
    setError("");

    const lat = parseFloat(latitude);
    const lng = parseFloat(longitude);
    if (isNaN(lat) || isNaN(lng)) {
      setError("위도/경도를 숫자로 입력해주세요.");
      return;
    }

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
      <Input
        placeholder="위도 (Latitude)"
        value={latitude}
        onChange={(e) => setLatitude(e.target.value)}
        disabled={isPending}
      />
      <Input
        placeholder="경도 (Longitude)"
        value={longitude}
        onChange={(e) => setLongitude(e.target.value)}
        disabled={isPending}
      />

      {error && <div className="text-sm text-red-500">{error}</div>}

      <Button
        onClick={handleSubmit}
        disabled={isPending || !name || !latitude || !longitude}
        variantIntent="primary"
      >
        {isPending ? "추가 중..." : "추가"}
      </Button>
    </div>
  );
}
