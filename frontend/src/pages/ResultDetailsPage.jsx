import React, {useState, useEffect} from 'react'
import {useParams} from 'react-router-dom'
import '../css/ResultDetailsPage.css'
import Divider from '@mui/material/Divider';
import {base_url} from '../api/api.js'

function ResultDetailsPage({result}){
    const {id} = useParams();
    
    const [recipeContent, setRecipeContent] = useState(null);

    useEffect(()=>{
        if(!id) return;

        fetch(`${base_url}/recipes/${id}`)
            .then(res => res.json())
            .then(data => setRecipeContent(data))
            .catch(error => console.error("Failed to get recipe content!", error))
    },[id])

    if(!recipeContent){
        return <div>Loading Recipe Content!</div>
    }

    return(

    <div className = "resultpage">
        <div className="result-details">

          <div className="img-cover">
                <img src={recipeContent.image_url} alt="" />
            </div> 

            <div className="recipe-title">
                <h1>{recipeContent.title}</h1>
            </div>
            
           <Divider sx={{backgroundColor:"rgb(89,54,45)"}} />
            
            <div className="recipe-content">
                <p>Cooking Time: {recipeContent.prep_time_minutes}</p>
                <div className="dietary-tag">
                        Dietary-tag:
                <ul style={{marginLeft:"7%"}}>
                
                {recipeContent.dietary_tags.map((dietaryTag)=>(
                    <li key={dietaryTag.id}>{dietaryTag.name}</li>
               ))}
                </ul>
               </div>
                <div className="ingredient-lists">
                    Ingredient:
                    <ul style={{marginLeft:"7%"}}>
                        {recipeContent.ingredients.map((ingredient)=>(
                            <li key={ingredient.id}>{ingredient.name}</li>
                        ))}
                    </ul>
                </div>
                <p>Instructions:</p>
                <p>{recipeContent.instructions}</p>
            </div> 

        </div>
    </div>
    )
}

export default ResultDetailsPage;