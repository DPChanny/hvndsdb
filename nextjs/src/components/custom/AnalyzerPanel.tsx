"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { Button } from "@/components/ui/Button";
import Image from "next/image";

type SessionData = {
  session_id: string;
};
type AroundFrameData = { frame: string; session_id: string };
type CenterFrameData = { frame: string; session_id: string };
type ProgressData = { progress: string; session_id: string };

type ClientMessage =
  | { type: "start_session_request"; data: SessionData }
  | { type: "cancel_deblur_gs"; data: SessionData }
  | { type: "end_session_request"; data: SessionData };

type ServerMessage =
  | { type: "progress"; data: ProgressData }
  | { type: "around_frame"; data: AroundFrameData }
  | { type: "center_frame"; data: CenterFrameData }
  | { type: "start_session"; data: SessionData }
  | { type: "end_session"; data: SessionData };

type AnalyzerPanelProps = {
  ws: WebSocket | null;
  isConnected: boolean;
  buildingId: string;
  onClose: () => void;
};

export function AnalyzerPanel({
  ws,
  isConnected,
  buildingId,
  onClose,
}: AnalyzerPanelProps) {
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [progressLog, setProgressLog] = useState<string[]>([]);
  const [aroundImage, setAroundImage] = useState<string | null>(null);
  const [centerImage, setCenterImage] = useState<string | null>(null);
  const logRef = useRef<HTMLDivElement>(null);

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
            setProgressLog([]);
            setAroundImage(null);
            setCenterImage(null);
            break;
          case "end_session":
            setIsSessionActive(false);
            onClose();
            break;
          case "progress":
            setProgressLog((prev) => [...prev, msg.data.progress]);
            break;
          case "around_frame":
            setAroundImage(`data:image/jpeg;base64,${msg.data.frame}`);
            break;
          case "center_frame":
            setCenterImage(`data:image/jpeg;base64,${msg.data.frame}`);
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

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [progressLog]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <Button
            onClick={() =>
              sendMessage({
                type: "cancel_deblur_gs",
                data: { session_id: buildingId },
              })
            }
            disabled={!isConnected}
            variantIntent="destructive"
            variantTone="outline"
          >
            멈춤
          </Button>
        </div>
      </div>

      {isSessionActive ? (
        <>
          <div
            className="bg-black text-green-400 p-4 h-64 overflow-auto font-mono text-sm break-words rounded"
            ref={logRef}
          >
            {progressLog.map((line, i) => (
              <div key={i}>{line}</div>
            ))}
          </div>

          <div className="grid grid-rows-2 gap-4">
            <ImageDisplay label="Around Frame" src={aroundImage} />
            <ImageDisplay label="Center Frame" src={centerImage} />
          </div>
        </>
      ) : (
        <p className="text-sm text-gray-500">세션을 기다리는 중입니다...</p>
      )}
    </div>
  );
}

function ImageDisplay({ label, src }: { label: string; src: string | null }) {
  return (
    <div>
      <h3 className="text-sm font-semibold mb-1">{label}</h3>
      <div className="aspect-[16/9] bg-black flex items-center justify-center border rounded">
        {src ? (
          <Image
            src={src}
            alt={label}
            width={960}
            height={540}
            layout="responsive"
            unoptimized
          />
        ) : (
          <span className="text-gray-400 text-sm">준비 중...</span>
        )}
      </div>
    </div>
  );
}
