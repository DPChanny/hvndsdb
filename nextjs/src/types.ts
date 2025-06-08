export type Building = {
  building_id: string;
  name: string;
  latitude: number;
  longitude: number;
};

export type BuildingDetail = {
  building_id: string;
  name: string;
  latitude: number;
  longitude: number;
  sample: boolean;
  frames: boolean;
  colmap: boolean;
  deblur_gs: boolean;
  ply: boolean;
  analyzing: boolean;
};

export type BuildingListResponseDTO = {
  success: boolean;
  code: number;
  message: string;
  data: Building[];
};

export type BuildingDetailResponseDTO = {
  success: boolean;
  code: number;
  message: string;
  data: BuildingDetail;
};
