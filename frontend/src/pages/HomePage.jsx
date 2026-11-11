import React, {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import '../css/HomePage.css'
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import AddIcon from '@mui/icons-material/Add';
import {base_url} from '../api/api.js'

function HomePage(){

    const [preview, setPreview] = useState(null);
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    //create a local url for preview
    const handleFileChange = (e) =>{
        const file = e.target.files[0];
        if (file){
            const url = URL.createObjectURL(file);
            setPreview(url);
            setFile(file);
            setError("");
        }
    };

    const navigate = useNavigate();

    //uploads the photo to /scan and opens the results -Arun
    const handleResult = async () =>{
        if (!file){
            setError("Choose a photo first.");
            return;
        }
        setLoading(true);
        setError("");
        try{
            const response = await fetch(`${base_url}/scan`, {
                method: "POST",
                headers: {"Content-Type": file.type || "application/octet-stream"},
                body: file,
            });
            const data = await response.json();
            if (!response.ok){
                throw new Error(data.detail || "Could not read the photo.");
            }
            navigate("/result", {state: {items: data.items}});
        }catch(err){
            setError(err.message);
        }finally{
            setLoading(false);
        }
    };

    return(
   
        <div className="homepage">

            <div className="header">
                <h1>Recipe Recommender</h1>
            </div>

            <h2>Don't Know What to Cook? We've Got You!</h2>
            <h3>Simply snap a photo of your ingredients and discover delicious recipes youe can make!</h3>

            {/*simple camera & upload a picture*/}  
            <div className="capture-upload">
                <div className = "snap-photo">
                <input id = "file-upload" type ="file" accept="image/*" onChange = {handleFileChange}/>
                <label htmlFor="file-upload" className="capture">
                    <CameraAltIcon sx={{fontSize:70 ,
                            border: '1px solid rgba(255, 255, 255, 0.3)',
                            borderRadius:'5px',
                            backgroundColor: 'rgba(255, 255, 255, 0.08)',
                            backdropFilter: 'blur(3px)',

                            '&:hover': {
                            color: '#fff',
                            backgroundColor: 'rgba(255, 255, 255, 0.18)',
                            borderColor: 'rgba(255, 255, 255, 0.6)',
                            },
                            
                            '&:active':{
                                transform: 'scale(0.95)',
                            }
                    
                    }} />
                 </label>
                <label htmlFor="file-upload" className="choose-file">
                     <AddIcon sx={{fontSize:70,
                            color: 'rgba(255, 255, 255, 0.8)',
                            border: '1px solid rgba(255, 255, 255, 0.3)',
                            borderRadius:'5px',
                            backgroundColor: 'rgba(255, 255, 255, 0.08)',
                            backdropFilter: 'blur(3px)',

                            '&:hover': {
                            color: '#fff',
                            backgroundColor: 'rgba(255, 255, 255, 0.18)',
                            borderColor: 'rgba(255, 255, 255, 0.6)',
                            },

                            '&:active':{
                                transform: 'scale(0.95)',
                            }

                     }}/>
                 </label>
                     </div>

                  <sub>Snap your ingredients</sub>

                <div className = "preview-section">          
                {preview && (
                    <>
                    <h3>Image Preview: </h3>
                    <img
                        src={preview}
                        alt="Preview"
                        style={{maxWidth : '200px'}} 
                    />
                    </>
                )}
                </div>
            </div>

        
            {/*submit*/} 
            <div className="submit-button">
                <button className="button-icon" onClick={handleResult} disabled={loading}>
                    {loading ? "Finding ingredients..." : "Generate Recipe"}
                </button>
                {error && <p role="alert">{error}</p>}
            </div>


        </div>
    );
}

export default HomePage;