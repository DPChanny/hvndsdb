import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BuildingListResponseDTO, BuildingDetailResponseDTO } from "@/types";

const API_BASE_URL = "http://localhost:8000/api/building";

export const useBuildingList = () => {
  return useQuery<BuildingListResponseDTO>({
    queryKey: ["building"],
    queryFn: async () => {
      const res = await fetch(API_BASE_URL);
      if (!res.ok) throw new Error("Failed to fetch buildings");
      const data = await res.json();
      console.log("Fetched buildings:", data);
      return data;
    },
  });
};

export const useBuildingDetail = (buildingId: string | null) => {
  return useQuery<BuildingDetailResponseDTO>({
    queryKey: ["building", buildingId],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/${buildingId}`);
      if (!res.ok) throw new Error("Failed to fetch building detail");
      const data = await res.json();
      console.log("Fetched building detail:", data);
      return data;
    },
    enabled: !!buildingId,
  });
};

export const useAddBuilding = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (body: {
      name: string;
      latitude: number;
      longitude: number;
    }): Promise<BuildingDetailResponseDTO> => {
      const res = await fetch(API_BASE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        throw new Error("Failed to add building");
      }

      const data = await res.json();
      return data;
    },

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["building"] });
    },
  });
};

type UseSampleUploadOptions = {
  buildingId: string;
  onSuccess?: () => void;
  onError?: (e: Error) => void;
};

export function useSampleUpload({
  buildingId,
  onSuccess,
  onError,
}: UseSampleUploadOptions) {
  const mutation = useMutation({
    mutationFn: async (file: File) => {
      const res = await fetch(`${API_BASE_URL}/${buildingId}/sample`);
      const json = await res.json();

      if (!json.success) throw new Error(json.message);
      const uploadUrl = json.data as string;

      const uploadRes = await fetch(uploadUrl, {
        method: "PUT",
        body: file,
        headers: {
          "Content-Type": "video/mp4",
        },
      });

      if (!uploadRes.ok) throw new Error("업로드 실패");
    },
    onSuccess,
    onError,
  });

  return () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "video/mp4";

    input.onchange = () => {
      const file = input.files?.[0];
      if (file) mutation.mutate(file);
    };

    input.click();
  };
}
