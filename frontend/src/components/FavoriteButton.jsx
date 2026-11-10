import Checkbox from '@mui/material/Checkbox';
import FavoriteBorder from '@mui/icons-material/FavoriteBorder';
import Favorite from '@mui/icons-material/Favorite';
import {base_url} from '../api/api.js'

function FavoriteButton({recipe,favorites,setFavorites}){
    const label = { slotProps: { input: { 'aria-label': 'Checkbox demo' } } };

        //use for checkedbox
    const  isFavorite = favorites.some((favorite)=>favorite.recipe_id === recipe.id)
            
        const handleFavorites = async (kind,recipe_id,checked) => {

            const savedToken = localStorage.getItem("token");

            try{
                let response;
                
                if(checked == true){
                response = await fetch(
                    `${base_url}/saved-recipes/${kind}/${recipe_id}`,
                    {
                        method:"PUT",
                        headers:{
                            Authorization:`Bearer ${savedToken}`
                        }
                    }
                );
                }else{
                 response = await fetch(
                    `${base_url}/saved-recipes/${kind}/${recipe_id}`,
                    {
                        method:"DELETE",
                        headers:{
                            Authorization:`Bearer ${savedToken}`
                        }
                    } 
                );                  
                }

                if (!response.ok){
                    throw new Error ("Failed to save favorite!");
                }

               
                if (checked) {
                setFavorites((prev) =>
                    prev.some((recipe)=>(recipe.recipe_id)===recipe_id)
                    ? prev
                    :[...prev, {recipe_id:recipe_id, recipe:recipe}]);
                    } else {
                setFavorites((prev) =>
                    prev.filter((favorite) => (favorite.recipe_id) !== (recipe_id))
                );
                }

            
            }catch (error){
                console.log(error.message);
            }

        
        };

  
    return (
        <>
            <Checkbox 
                {...label} 
                icon={<FavoriteBorder sx={{color:"rgb(89,45,59)", 
                                            '&:hover':{color:"rgb(89,45,59)"}}}/>} 
                checkedIcon={<Favorite sx={{color:"rgb(89,45,59)"}} />}
                checked = {isFavorite} 
                onChange={(e)=>{
                    handleFavorites("favorite",recipe.id,e.target.checked);
                }}        
            />
        </>
    );
}

export default FavoriteButton;