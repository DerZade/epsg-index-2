interface EPSG {
    code: number;
    name: string;
    wkt: string | null;
    proj4: string | null;
    bbox: [number, number, number, number] | null;
    unit: string | null;
    area: string | null;
    accuracy: number | null;
    deprecated: boolean;
}
