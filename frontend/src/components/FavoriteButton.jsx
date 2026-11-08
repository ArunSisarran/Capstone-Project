import Checkbox from '@mui/material/Checkbox';
import FavoriteBorder from '@mui/icons-material/FavoriteBorder';
import Favorite from '@mui/icons-material/Favorite';


function FavoriteButton({recipe,favorites,setFavorites}){
    const label = { slotProps: { input: { 'aria-label': 'Checkbox demo' } } };

        //use for checkedbox
       const  isFavorite = favorites.some((favorite) => favorite.id === recipe.id);
       
        const newFavorites = {
            id:recipe.id,
            title:recipe.title,
            image_url:recipe.image_url,
            viewedAt:new Date(). toISOString(),
        };
        const handleFavorites = () =>{
         favorites = JSON.parse(localStorage.getItem("clickFavorites") || "[]");

         const checked = favorites.some((item) => item.id === recipe.id);

        const addNewFavorites = checked
            ? favorites.filter((item) => item.id != recipe.id)
        
            :[
            newFavorites,
            ...favorites
            ];
        localStorage.setItem("clickFavorites", JSON.stringify(addNewFavorites));

        //console.log("Favorite id:", addNewFavorites);

        setFavorites(addNewFavorites)
    };
    return (
        <>
            <Checkbox 
                {...label} 
                icon={<FavoriteBorder sx={{color:"rgb(89,45,59)", 
                                            '&:hover':{color:"rgb(89,45,59)"}}}/>} 
                checkedIcon={<Favorite  color="error"/>}
                checked = {isFavorite} 
                onChange={handleFavorites}        
            />
        </>
    );
}

export default FavoriteButton;