"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import Image from "next/image";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

type SessionData = { session_id: string };
type FrameData = { frame: string; session_id: string };

type ClientMessage =
  | { type: "start_session_request"; data: SessionData }
  | { type: "end_session_request"; data: SessionData }
  | { type: "frame"; data: FrameData };

type ServerMessage =
  | { type: "start_session"; data: SessionData }
  | { type: "end_session"; data: SessionData }
  | { type: "frame"; data: FrameData }
  | { type: "frame_complete"; data: SessionData };

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
  const [mode, setMode] = useState<"video" | "realtime">("realtime");
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [frameImage, setFrameImage] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const streamRef = useRef<MediaStream | null>(null);
  const latestVideoFrameRef = useRef<HTMLVideoElement | null>(null);
  const pendingVideoFrames = useRef<string[]>([]);
  const isSendingVideoFrame = useRef(false);

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
            stopStream();
            onClose();
            break;
          case "frame":
            setFrameImage(`data:image/jpeg;base64,${msg.data.frame}`);
            break;
          case "frame_complete":
            if (mode === "video") {
              const nextFrame = pendingVideoFrames.current.shift();
              if (nextFrame) {
                sendMessage({
                  type: "frame",
                  data: { session_id: buildingId, frame: nextFrame },
                });
              } else {
                isSendingVideoFrame.current = false;
              }
            } else if (mode === "realtime") {
              sendRealtimeFrame();
            }
            break;
        }
      } catch (err) {
        console.error("WebSocket 메시지 파싱 실패:", event.data, err);
      }
    };

    ws.addEventListener("message", handleMessage);
    sendMessage({
      type: "start_session_request",
      data: { session_id: buildingId },
    });

    return () => {
      ws.removeEventListener("message", handleMessage);
      stopStream();
    };
  }, [ws, buildingId, sendMessage, onClose, mode]);

  const stopStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  };

  const handleVideoUpload = async (file: File) => {
    setIsUploading(true);
    const videoURL = URL.createObjectURL(file);
    const video = document.createElement("video");
    video.src = videoURL;
    video.crossOrigin = "anonymous";
    video.muted = true;

    await new Promise((res) =>
      video.addEventListener("loadedmetadata", () => res(null))
    );
    await video.play();

    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const fps = 30;
    const interval = 1000 / fps;
    const duration = video.duration * 1000;
    const totalFrames = Math.floor(duration / interval);

    for (let i = 0; i < totalFrames; i++) {
      const time = i * interval;

      await new Promise<void>((res) => {
        const seekHandler = () => {
          requestAnimationFrame(() => {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            const base64 = canvas.toDataURL("image/jpeg").split(",")[1];
            pendingVideoFrames.current.push(base64);
            if (
              !isSendingVideoFrame.current &&
              pendingVideoFrames.current.length > 0
            ) {
              isSendingVideoFrame.current = true;
              const nextFrame = pendingVideoFrames.current.shift();
              if (nextFrame) {
                sendMessage({
                  type: "frame",
                  data: { session_id: buildingId, frame: nextFrame },
                });
              }
            }
            res();
          });
        };
        video.addEventListener("seeked", seekHandler, { once: true });
        video.currentTime = time / 1000;
      });
    }

    video.pause();
    URL.revokeObjectURL(videoURL);
    setIsUploading(false);
  };

  const sendRealtimeFrame = () => {
    if (!latestVideoFrameRef.current || !ws) return;

    const video = latestVideoFrameRef.current;
    const canvas = document.createElement("canvas");
    canvas.width = 640;
    canvas.height = 480;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    ws.send(
      JSON.stringify({
        type: "frame",
        data: {
          session_id: buildingId,
          frame: canvas.toDataURL("image/jpeg").split(",")[1],
        },
      })
    );
  };

  const handleRealtimeStreaming = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    streamRef.current = stream;

    const video = document.createElement("video");
    video.srcObject = stream;
    video.muted = true;
    await video.play();

    latestVideoFrameRef.current = video;
    sendRealtimeFrame();
  };

  useEffect(() => {
    if (mode === "realtime" && isSessionActive) {
      handleRealtimeStreaming();
    }
  }, [mode, isSessionActive]);

  const handleVideoUploadWrapper = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0];
    if (!file || !isSessionActive || !ws || ws.readyState !== WebSocket.OPEN)
      return;

    stopStream();
    setMode("video");

    await handleVideoUpload(file);

    isSendingVideoFrame.current = false;
    pendingVideoFrames.current = [];

    setMode("realtime");
    await handleRealtimeStreaming();
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <Input
          type="file"
          accept="video/*"
          onChange={handleVideoUploadWrapper}
          disabled={!isSessionActive || isUploading}
        />
      </div>

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
