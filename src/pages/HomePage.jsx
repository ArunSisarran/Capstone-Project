import React from 'react';
import {useState} from 'react'
import {useNavigate} from 'react-router-dom';
import '../pages/HomePage.css'
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import AddIcon from '@mui/icons-material/Add';

function HomePage(){

    const [preview, setPreview] = useState(null);

    

    //create a local url for preview
    const handleFileChange = (e) =>{
        const file = e.target.files[0];
        if (file){
            const url = URL.createObjectURL(file);
            setPreview(url);
        }
    };

    const navigate = useNavigate();
    return(
   
        <div className="homepage">

            <div className="header">
                <h1>Recipe Recommender</h1>
            </div>

            <h3>[Description]</h3>

            {/*simple camera & upload a picture*/}  
            <div className="capture-upload">
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
                            }

                     }}/>
                 </label>

                                
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

            <sub>Take or Upload a picture of your ingredients</sub>

            {/*submit*/} 
            <div className="submit-button">
                <button className="button-icon" onClick={()=>navigate("/result")}>Generate Recipe</button>
            </div>


        </div>
    );
}

export default HomePage;