"use client";

import { useEffect, useState, useCallback } from "react";
import Image from "next/image";
import { Button } from "@/components/ui/Button";

type SessionData = {
  session_id: string;
};

type FrameData = { frame: string; session_id: string };

type ClientMessage =
  | { type: "start_session_request"; data: SessionData }
  | { type: "end_session_request"; data: SessionData }
  | { type: "frame"; data: FrameData };

type ServerMessage =
  | { type: "start_session"; data: SessionData }
  | { type: "end_session"; data: SessionData }
  | { type: "frame"; data: FrameData };

type ViewerPanelProps = {
  ws: WebSocket | null;
  isConnected: boolean;
  buildingId: string;
  onClose: () => void;
};

export function ViewerPanel({
  ws,
  isConnected,
  buildingId,
  onClose,
}: ViewerPanelProps) {
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [frameImage, setFrameImage] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const sendMessage = useCallback(
    (message: ClientMessage) => {
      if (ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(message));
      }
    },
    [ws]
  );

  useEffect(() => {
    if (!ws) return;

    const handleMessage = (event: MessageEvent<string>) => {
      try {
        const msg: ServerMessage = JSON.parse(event.data);
        if (msg.data.session_id !== buildingId) return;

        switch (msg.type) {
          case "start_session":
            setIsSessionActive(true);
            setFrameImage(null);
            break;
          case "end_session":
            setIsSessionActive(false);
            onClose();
            break;
          case "frame":
            setFrameImage(`data:image/jpeg;base64,${msg.data.frame}`);
            break;
        }
      } catch {
        console.error("Invalid WebSocket message:", event.data);
      }
    };

    ws.addEventListener("message", handleMessage);

    sendMessage({
      type: "start_session_request",
      data: { session_id: buildingId },
    });

    return () => {
      ws.removeEventListener("message", handleMessage);
    };
  }, [ws, buildingId, sendMessage, onClose]);

  const handleVideoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !ws || ws.readyState !== WebSocket.OPEN || !isSessionActive)
      return;

    setIsUploading(true);
    const videoURL = URL.createObjectURL(file);

    const video = document.createElement("video");
    video.src = videoURL;
    video.crossOrigin = "anonymous";
    video.muted = true;

    await video.play();

    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const fps = 5;
    const interval = 1000 / fps;
    const duration = video.duration * 1000;

    for (let time = 0; time < duration; time += interval) {
      await new Promise((res) => {
        video.currentTime = time / 1000;
        video.onseeked = () => res(null);
      });

      ctx?.drawImage(video, 0, 0, canvas.width, canvas.height);
      const dataURL = canvas.toDataURL("image/jpeg");
      const base64 = dataURL.split(",")[1];

      ws.send(
        JSON.stringify({
          type: "frame",
          data: {
            session_id: buildingId,
            frame: base64,
          },
        })
      );
    }

    video.pause();
    URL.revokeObjectURL(videoURL);
    setIsUploading(false);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <input
          type="file"
          accept="video/*"
          onChange={handleVideoUpload}
          disabled={!isSessionActive || isUploading}
        />
        <Button
          onClick={() =>
            sendMessage({
              type: "end_session_request",
              data: { session_id: buildingId },
            })
          }
          disabled={!isConnected}
          variantIntent="destructive"
        >
          세션 종료
        </Button>
      </div>

      {isUploading && <p className="text-sm text-blue-500">업로드 중...</p>}

      {isSessionActive ? (
        <div className="space-y-4">
          <h3 className="text-sm font-semibold">Frame</h3>
          <div className="aspect-[16/9] bg-black flex items-center justify-center border rounded">
            {frameImage ? (
              <Image
                src={frameImage}
                alt="Frame"
                width={960}
                height={540}
                unoptimized
              />
            ) : (
              <span className="text-gray-400 text-sm">수신된 프레임 없음</span>
            )}
          </div>
        </div>
      ) : (
        <p className="text-sm text-gray-500">세션을 기다리는 중입니다...</p>
      )}
    </div>
  );
}
