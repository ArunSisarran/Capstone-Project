export const MAX_SIDE = 2048;

export class UnreadablePhotoError extends Error {
    constructor(heic){
        super(heic ? "heic" : "unreadable");
        this.heic = heic;
    }
}

const isHeic = (file) => /hei[cf]/i.test(file.type) || /\.hei[cf]$/i.test(file.name || "");

// re-encode as jpeg so heic (safari) and huge photos still upload -Arun
export async function prepareImage(file){
    let bitmap;
    try{
        bitmap = await createImageBitmap(file, {imageOrientation: "from-image"});
    }catch{
        throw new UnreadablePhotoError(isHeic(file));
    }
    const scale = Math.min(1, MAX_SIDE / Math.max(bitmap.width, bitmap.height));
    const canvas = document.createElement("canvas");
    canvas.width = Math.round(bitmap.width * scale);
    canvas.height = Math.round(bitmap.height * scale);
    canvas.getContext("2d").drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    bitmap.close();
    const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.88));
    if (!blob) throw new UnreadablePhotoError(false);
    return blob;
}
