import React from 'react'
import {useState} from 'react'
import { useNavigate } from "react-router-dom";
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import {Link} from 'react-router-dom'
import Divider from '@mui/material/Divider';
import Checkbox from '@mui/material/Checkbox';
import FavoriteBorder from '@mui/icons-material/FavoriteBorder';
import Favorite from '@mui/icons-material/Favorite';
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorder';
import BookmarkIcon from '@mui/icons-material/Bookmark';

function RecipeCard({recipe}){
    const label = { slotProps: { input: { 'aria-label': 'Checkbox demo' } } };
    const navigate = useNavigate();

    //local storage
    const handleView = () =>{
    
    const history = JSON.parse(localStorage.getItem("clickHistory") || "[]");

    const addNewHistory = [
        history.filter(item => item.id !== recipe.id)
    ];
    
    localStorage.setItem("clickHistory", JSON.stringify(addNewHistory));

    console.log("History id:", recipe.id);
    navigate(`/result/${recipe.id}`);


    };

    const handleFavorite = () =>{
    const favorites = JSON.parse(localStorage.getItem("clickFavorite") || "[]");

    const addNewFavorite =[
        {
            id:recipe.id,
            title:recipe.title,
        },
    ...favorites.filter(item => item.id !== recipe.id),
    ]

    localStorage.setItem("clickFavorite", JSON.stringify(addNewFavorite));

    console.log("Favorite id:", recipe.id);
        
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
                image= {recipe.imageUrl}
            />

            <CardContent>
                <Typography gutterBottom variant="h6" component="div" sx={{mb:0.5,textAlign:"center"}}>
                {recipe.title}
                </Typography>

                <Divider sx={{backgroundColor:"black"}} />

                <Typography component="div" variant="body2" sx={{ color: "rgb(89,45,59)", mt:1, ml:2 }}>
                Cooking Time: {recipe.time}
                <br></br>
                Cuisine: {recipe.cuisine}
                <br></br>
                Dietary-tag: {recipe.dietaryTag}
                <br></br>
                Ingredients:
                <ul style={{marginLeft:"20px"}}>
                    {recipe.ingredients.map((ingredient)=>(
                        <li key={ingredient}>{ingredient}</li>
                    ))}
                </ul>
                </Typography>
            </CardContent>

            <CardActions>

                <Checkbox {...label} icon={<FavoriteBorder sx={{color:"rgb(89,45,59)", '&:hover':{color:"rgb(89,45,59)"}}}/>} checkedIcon={<Favorite />} onClick={handleFavorite} />
                <Checkbox
                {...label}
                icon={<BookmarkBorderIcon sx={{color:"rgb(89,45,59)"}} />}
                checkedIcon={<BookmarkIcon xs={{color:"rgb(89,45,59)"}}/>}
                />

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