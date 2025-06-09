"use client";

import { useRouter, usePathname } from "next/navigation";
import { useBuildingDetail } from "@/hooks/building";
import { useSampleUpload } from "@/hooks/building";
import { Button } from "@/components/ui/Button";

type Props = {
  buildingId: string;
};

export function BuildingPanel({ buildingId }: Props) {
  const { data, isLoading } = useBuildingDetail(buildingId);
  const router = useRouter();
  const pathname = usePathname();

  const handleSampleUpload = useSampleUpload({
    buildingId,
    onSuccess: () => {
      alert("업로드 성공");
      router.refresh();
    },
    onError: (e: { message: string }) => {
      alert(`업로드 실패: ${e.message}`);
    },
  });

  if (isLoading || !data) return <p className="text-sm">로딩 중...</p>;

  const { sample, frames, colmap, deblur_gs, ply, analyzing } = data.data;

  const openAnalyzeModal = () =>
    router.push(`${pathname}?modal=analyze&buildingId=${buildingId}`);

  const openViewerModal = () =>
    router.push(`${pathname}?modal=viewer&buildingId=${buildingId}`);

  return (
    <div className="mt-4 space-y-6 text-sm">
      <div className="space-y-2">
        {sample ? (
          <FileItem
            name="sample.mp4"
            onDelete={() => console.log("delete sample")}
          />
        ) : (
          <Button
            variantIntent="primary"
            variantSize="sm"
            onClick={handleSampleUpload}
          >
            Sample 업로드
          </Button>
        )}

        {frames && (
          <FileItem
            name="frames.zip"
            onDelete={() => console.log("delete frames")}
          />
        )}
        {colmap && (
          <FileItem
            name="colmap.zip"
            onDelete={() => console.log("delete colmap")}
          />
        )}
        {deblur_gs && (
          <FileItem
            name="deblur_gs.zip"
            onDelete={() => console.log("delete deblur_gs")}
          />
        )}
        {ply && (
          <FileItem
            name="point_cloud.ply"
            onDelete={() => console.log("delete ply")}
          />
        )}
      </div>
      <div className="flex flex-wrap gap-3">
        {sample && (
          <>
            <Button
              variantIntent="secondary"
              variantSize="sm"
              onClick={openAnalyzeModal}
            >
              {analyzing ? "분석 중" : "분석 시작"}
            </Button>
            <Button
              variantIntent="secondary"
              variantSize="sm"
              onClick={openViewerModal}
            >
              안내 보기
            </Button>
          </>
        )}
      </div>
    </div>
  );
}

function FileItem({ name, onDelete }: { name: string; onDelete: () => void }) {
  return (
    <div className="flex items-center justify-between">
      <span className="font-semibold">{name}</span>
      <Button variantIntent="destructive" variantSize="sm" onClick={onDelete}>
        삭제
      </Button>
    </div>
  );
}
