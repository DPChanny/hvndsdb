"use client";

import { useRouter, usePathname } from "next/navigation";
import { useBuildingDetail } from "@/hooks/building";
import { useSampleUpload } from "@/hooks/building";
import { Button } from "@/components/ui/Button";
import { useState } from "react";

type Props = {
  buildingId: string;
};

export function BuildingPanel({ buildingId }: Props) {
  const { data, isLoading } = useBuildingDetail(buildingId);
  const router = useRouter();
  const pathname = usePathname();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);

  const handleSampleUpload = useSampleUpload({
    buildingId,
    onProgress: (percent) => {
      setIsUploading(true);
      setUploadProgress(percent);
    },
    onSuccess: () => {
      setIsUploading(false);
      setUploadProgress(null);
      router.replace(pathname);
    },
    onError: (e: { message: string }) => {
      setIsUploading(false);
      setUploadProgress(null);
      router.replace(pathname);
      setTimeout(() => alert(`업로드 실패: ${e.message}`), 100);
    },
  });

  if (isLoading || !data) return <p className="text-sm">로딩 중...</p>;

  const { sample, frames, colmap, deblur_gs, ply, analyzing, posenet } =
    data.data;

  const canOpenViewer = ply && posenet && !analyzing;

  const openAnalyzeModal = () =>
    router.push(`${pathname}?modal=analyze&buildingId=${buildingId}`);

  const openViewerModal = () =>
    router.push(`${pathname}?modal=viewer&buildingId=${buildingId}`);

  return (
    <div className="mt-4 space-y-6 text-sm">
      <div className="space-y-2">
        {sample ? (
          <div className="space-y-2">
            <FileItem
              name="sample.mp4"
              exists={sample}
              description="Sample Video"
              onDelete={() => console.log("delete sample")}
            />
            <FileItem
              name="frames.zip"
              exists={frames}
              description="Frames extracted from Sample Video"
              onDelete={() => console.log("delete frames")}
            />
            <FileItem
              name="colmap.zip"
              exists={colmap}
              description="COLMAP Reconstruction Data"
              onDelete={() => console.log("delete colmap")}
            />
            <FileItem
              name="deblur_gs.zip"
              exists={deblur_gs}
              description="Deblur GS Training Data"
              onDelete={() => console.log("delete deblur_gs")}
            />
            <FileItem
              name="point_cloud.ply"
              exists={ply}
              description="Deblur GS Training Result"
              onDelete={() => console.log("delete ply")}
            />
            <FileItem
              name="posenet.zip"
              exists={posenet}
              description="PoseNet Training Result"
              onDelete={() => console.log("delete posenet")}
            />
          </div>
        ) : (
          <div className="flex flex-col gap-2 w-full">
            <div className="flex items-center gap-2">
              <Button
                variantIntent="primary"
                variantSize="sm"
                onClick={handleSampleUpload}
                disabled={isUploading}
              >
                {uploadProgress !== null
                  ? `업로드 중... ${uploadProgress}%`
                  : "Sample 업로드"}
              </Button>
              {isUploading && (
                <span className="text-xs text-muted animate-pulse">
                  잠시만 기다려 주세요
                </span>
              )}
            </div>
            {uploadProgress !== null && (
              <div className="w-full bg-gray-200 rounded h-2">
                <div
                  className="bg-blue-500 h-2 rounded transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            )}
          </div>
        )}
      </div>
      <div className="flex flex-wrap gap-3">
        {sample && (
          <>
            <Button
              variantIntent="primary"
              variantSize="sm"
              onClick={openAnalyzeModal}
            >
              {analyzing ? "분석 중" : "분석 시작"}
            </Button>
            <Button
              variantIntent="primary"
              variantSize="sm"
              onClick={openViewerModal}
              disabled={!canOpenViewer}
            >
              안내 보기
            </Button>
          </>
        )}
      </div>
    </div>
  );
}
type FileItemProps = {
  name: string;
  exists: boolean;
  description: string;
  onDelete?: () => void;
};
function FileItem({ name, exists, description, onDelete }: FileItemProps) {
  return (
    <div
      className={`flex items-center justify-between p-3 rounded border text-sm ${
        exists
          ? "bg-green-50 border-green-300 text-green-800"
          : "bg-red-50 border-red-300 text-red-800"
      }`}
    >
      <div className="flex flex-row items-center gap-2 flex-wrap">
        <span className="font-semibold">{name}</span>
        <span className="text-xs text-muted">{description}</span>
      </div>
      <Button
        variantIntent="destructive"
        variantSize="sm"
        onClick={onDelete}
        disabled={!exists || !onDelete}
      >
        삭제
      </Button>
    </div>
  );
}
