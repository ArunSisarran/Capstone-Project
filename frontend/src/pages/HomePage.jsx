import {useEffect, useRef, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import PhotoCameraRounded from '@mui/icons-material/PhotoCameraRounded';
import ArrowForwardRounded from '@mui/icons-material/ArrowForwardRounded';
import IngredientTag from '../components/IngredientTag';
import '../css/HomePage.css'
import {base_url} from '../api/api.js'
import {prepareImage, UnreadablePhotoError} from '../utils/prepareImage.js'
import sampleFridge from '../assets/sample-fridge.jpg'

// x/y are % of the frame -Arun
const EXAMPLE_TAGS = [
    {name: "Parsley", category: "Produce", x: 80, y: 12},
    {name: "Apple", category: "Produce", x: 16, y: 50},
    {name: "Tomato", count: 2, category: "Produce", x: 52, y: 52},
    {name: "Yogurt", category: "Dairy", x: 19, y: 79},
];

const NOT_A_PHOTO = "That file isn't a photo we can read. Try a JPEG or PNG.";
const HEIC_PHOTO = "This browser can't open iPhone HEIC photos. Open this page in Safari, or on your iPhone set Settings › Camera › Formats to Most Compatible.";
const SCANNER_DOWN = "The scanner isn't available right now. Try again in a minute.";
const SCAN_ERRORS = {
    400: NOT_A_PHOTO,
    413: "That photo is too large. Try a smaller one.",
    429: "You've scanned a lot in the last minute. Wait a moment, then try again.",
};
// backend waits up to 30 s for the detector -Arun
const SCAN_TIMEOUT_MS = 35000;

function HomePage(){

    const [preview, setPreview] = useState(null);
    const [file, setFile] = useState(null);
    const [preparing, setPreparing] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");
    const [dragging, setDragging] = useState(false);
    const inputRef = useRef(null);
    const scanRef = useRef(null);
    const navigate = useNavigate();

    useEffect(() => () => preview && URL.revokeObjectURL(preview), [preview]);
    useEffect(() => () => scanRef.current?.abort(), []);

    const pickFile = async (picked, extraCount = 0) =>{
        if (!picked) return;
        setError("");
        setNotice(extraCount > 0 ? "We'll use the first photo. Scan one photo at a time." : "");
        if (!picked.type.startsWith("image/") && !/\.hei[cf]$/i.test(picked.name)){
            setError(NOT_A_PHOTO);
            return;
        }
        setPreparing(true);
        try{
            const jpeg = await prepareImage(picked);
            setPreview(URL.createObjectURL(jpeg));
            setFile(jpeg);
        }catch(err){
            setError(err instanceof UnreadablePhotoError && err.heic ? HEIC_PHOTO : NOT_A_PHOTO);
        }finally{
            setPreparing(false);
        }
    };

    const busy = loading || preparing;
    const openPicker = () => !busy && inputRef.current?.click();

    const handleDrop = (e) =>{
        e.preventDefault();
        setDragging(false);
        const files = e.dataTransfer.files;
        if (!busy) pickFile(files[0], files.length - 1);
    };

    const handleResult = async () =>{
        if (!file){
            setError("Choose a photo first.");
            return;
        }
        const scan = new AbortController();
        scanRef.current = scan;
        const timer = setTimeout(() => scan.abort("timeout"), SCAN_TIMEOUT_MS);
        setLoading(true);
        setError("");
        setNotice("");
        try{
            const response = await fetch(`${base_url}/scan`, {
                method: "POST",
                headers: {"Content-Type": "image/jpeg"},
                body: file,
                signal: scan.signal,
            });
            if (!response.ok){
                throw new Error(SCAN_ERRORS[response.status] || SCANNER_DOWN);
            }
            const data = await response.json();
            navigate("/result", {state: {items: data.items, suggestions: data.suggestions, vlm: data.vlm}});
        }catch(err){
            // user cancel stays silent -Arun
            if (scan.signal.aborted){
                if (scan.signal.reason === "timeout") setError("The scan took too long. Try again in a minute.");
            }else{
                setError(err instanceof TypeError ? SCANNER_DOWN : err.message);
            }
        }finally{
            clearTimeout(timer);
            scanRef.current = null;
            setLoading(false);
        }
    };

    const frameLabel = loading ? "Scanning…" : preparing ? "Opening…" : file ? "Ready" : "Example scan";

    return(
        <main className="home">

            <section className="home-head">
                <Typography variant="display" component="h1">What's in your fridge?</Typography>
                <Typography className="home-lead">
                    Snap a photo of your fridge or pantry. We'll spot the ingredients and find recipes you can make with them.
                </Typography>
            </section>

            <section className="home-scan" aria-label="Scan a photo">
                {/* reset so the same photo can be picked again -Arun */}
                <input ref={inputRef} type="file" accept="image/*,.heic,.heif" hidden
                       onChange={(e) => {pickFile(e.target.files[0]); e.target.value = "";}}/>

                {/* keyboard users use the button below -Arun */}
                <div className={`scan-frame${preview ? "" : " is-example"}${dragging ? " is-dragging" : ""}${loading ? " is-scanning" : ""}`}
                     onClick={openPicker}
                     onDragOver={(e) => {e.preventDefault(); setDragging(true);}}
                     onDragLeave={() => setDragging(false)}
                     onDrop={handleDrop}>
                    {preview ? (
                        <img src={preview} alt="Your photo" className="scan-frame__photo"/>
                    ) : (
                        <>
                            <img src={sampleFridge} className="scan-frame__photo scan-frame__photo--example"
                                 alt="Example scan: a fridge with an apple, tomatoes, parsley and yogurt, each marked with a tag."/>
                            {EXAMPLE_TAGS.map((t) => (
                                <span key={t.name} className="scan-frame__pin" style={{left: `${t.x}%`, top: `${t.y}%`}} aria-hidden="true">
                                    <IngredientTag name={t.name} count={t.count} category={t.category}/>
                                </span>
                            ))}
                            <span className="scan-frame__drop" aria-hidden="true">{dragging ? "Drop to use this photo" : "Drop or click to use your photo"}</span>
                        </>
                    )}
                    <span className="scan-frame__label">{frameLabel}</span>
                </div>

                <div className="scan-actions">
                    {file ? (
                        <>
                            <Button size="large" fullWidth onClick={handleResult} disabled={loading}
                                    endIcon={loading ? <CircularProgress size={18} color="inherit"/> : <ArrowForwardRounded/>}>
                                {loading ? "Looking for ingredients" : "Find recipes"}
                            </Button>
                            {loading ? (
                                <Button variant="text" onClick={() => scanRef.current?.abort()}>Cancel</Button>
                            ) : (
                                <Button variant="text" onClick={openPicker} disabled={preparing}>Choose another photo</Button>
                            )}
                        </>
                    ) : (
                        <Button size="large" fullWidth onClick={openPicker} disabled={preparing} startIcon={<PhotoCameraRounded/>}>
                            Take or upload a photo
                        </Button>
                    )}
                </div>

                <p className="scan-status" aria-live="polite">
                    {loading ? "Looking for ingredients. This usually takes under 10 seconds."
                        : preparing ? "Opening your photo." : ""}
                </p>
                {notice && <Alert severity="info">{notice}</Alert>}
                {error && <Alert severity="error">{error}</Alert>}
            </section>

            <section className="home-how" aria-labelledby="how-title">
                <Typography variant="h2" id="how-title">How it works</Typography>
                <ol className="how-steps">
                    <li><span><strong>Snap</strong> your fridge with the door open and the light on.</span></li>
                    <li><span><strong>See</strong> the ingredients we found.</span></li>
                    <li><span><strong>Pick</strong> a recipe. The best matches come first.</span></li>
                </ol>
            </section>

        </main>
    );
}

export default HomePage;
