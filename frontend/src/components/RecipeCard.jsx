import React, {useState}from 'react'
import {Link, useNavigate } from "react-router-dom";
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import Stack from '@mui/material/Stack'
import FavoriteButton from './FavoriteButton'
import SavedForLaterButton from './SavedForLaterButton'

function RecipeCard({recipe,history,setHistory,favorites,setFavorites, savedforlater,setSavedForLater}){

    const label = { slotProps: { input: { 'aria-label': 'Checkbox demo' } } };


    const navigate = useNavigate();

        const newHistory = {
            id:recipe.id,
            title:recipe.title,
            viewedAt:new Date(). toISOString(),
        };
    //local storage for adding on history
    const handleView = () => {
        history = JSON.parse(localStorage.getItem("clickHistory") || "[]");
        
        //add a new history on the top
        const addNewHistory = [
            newHistory,
            ...history.filter(item => item.id !== recipe.id)
        ].slice(0,10);

        //store on localstorage
        localStorage.setItem("clickHistory", JSON.stringify(addNewHistory));


        console.log("History id:",recipe.id);
        navigate(`/result/${recipe.id}`);
    };    

    return (
        <Card sx={{ width:"100%", 
                    maxWidth: 345, 
                    border:"1px solid rgb(89,45,59)", 
                    boxSizing:"border-box"
                  }}>

            <CardMedia
                component="img"
                alt={recipe.title}
                height="200"
                image= {recipe.image_url}
            />

            <CardContent>
                <Typography gutterBottom variant="h6" component="div" sx={{mb:0.5,textAlign:"center"}}>
                {recipe.title}
                </Typography>

                <Divider sx={{backgroundColor:"black"}} />

                <Typography component="div" variant="body2" sx={{ color: "rgb(89,45,59)", mt:1, ml:2 }}>      
                {/*if could not find the prep time in new object, then it would not shown below info for favorite and saved for late page  */}

                Cooking Time: {(recipe.prep_time_minutes||[])}
                      


                {
                    recipe.dietary_tags.length === 0 ? (
                        <div>Dietary-tag: None</div>
                    ):(
                        <> 
                        <Stack direction = "row" spacing = {1}> 
                        <div>Dietary-tag:</div> 
                        {(recipe.dietary_tags).map((dietaryTag)=>(
                        <div key={dietaryTag.id}> {dietaryTag.name} </div>
                        ))}
                        </Stack>
                        </>
                    )
}
                Ingredients:
                <ul style={{marginLeft:"20px"}}>
                    {(recipe.ingredients||[]).map((ingredient)=>(
                        <li key={ingredient.id}>{ingredient.name}</li>
                    ))}
                   
                </ul>
                

                    
                

            </Typography>

            </CardContent>

            <CardActions>
                {/*FAVORITE AND SAVED FOR LATER LIST ICONS */}
                <FavoriteButton recipe={recipe} favorites={favorites} setFavorites={setFavorites} />
                <SavedForLaterButton recipe={recipe} savedforlater={savedforlater} setSavedForLater={setSavedForLater} />


                <Button 
                    size="small" 
                    //component={Link} to = {`/result/${recipe.id}`}
                    sx={{
                        color:"rgb(89,45,59)",
                        border:"1px solid rgb(89,45,59)",
                    }}
                    onClick = {handleView}
                >
                        View Full Recipe
                </Button>

            </CardActions>
        </Card>
    )
}

export default RecipeCard;