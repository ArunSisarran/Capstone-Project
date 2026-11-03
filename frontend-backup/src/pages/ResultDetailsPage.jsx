import React from 'react'
import {useParams} from 'react-router-dom'
import {mockData} from '../mock/mockdata.js'
import '../pages/ResultDetailsPage.css'

function ResultDetailsPage(){
    const {id} = useParams();
    
    const recipeContent = mockData.recommendations.find(
        (recipeContent) => recipeContent.id === Number(id)
    );

    return(

    <div className = "resultpage">
        <div className="result-details">

            <div className="img-cover">
                <img src={recipeContent.imageUrl} alt="" />
            </div>

            <div className="recipe-title">
                <h1>{recipeContent.title}</h1>
            </div>

            <div className="recipe-content">
                <p>Cooking Time: {recipeContent.time}</p>
                <p>Cuisine:{recipeContent.cuisine}</p>
                <p>Dietary-tag:{recipeContent.dietaryTag}</p>
                <div className="ingredient-lists">
                    Ingredient:
                    <ul style={{marginLeft:"10%"}}>
                        {recipeContent.ingredients.map((ingredient)=>(
                            <li key={ingredient}>{ingredient}</li>
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