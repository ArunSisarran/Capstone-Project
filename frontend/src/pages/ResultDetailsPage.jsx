import React from 'react'
import {useParams} from 'react-router-dom'
import {mockData} from '../mock/mockdata.js'
import '../css/ResultDetailsPage.css'
import Divider from '@mui/material/Divider';

function ResultDetailsPage({result}){
    const {id} = useParams();
    
    const recipeContent = result.find(
        (recipeContent) => recipeContent.id === Number(id)
    );

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
                <p>Cuisine:{recipeContent.cuisine}</p>
               <p>Dietary-tag:
                {recipeContent.dietary_tags.map((dietaryTag)=>(
                    <p key={dietaryTag.id}>{dietaryTag.name}</p>
               ))}
               </p>
                <div className="ingredient-lists">
                    Ingredient:
                    <ul style={{marginLeft:"10%"}}>
                        {recipeContent.ingredients.map((ingredient)=>(
                            <li key={ingredient.id}>{ingredient.name}</li>
                        ))}
                    </ul>
                </div>
                <p>Instructions:</p>
              {/*  <p>{recipeContent.instructions}</p>*/}
            </div> 

        </div>
    </div>
    )
}

export default ResultDetailsPage;