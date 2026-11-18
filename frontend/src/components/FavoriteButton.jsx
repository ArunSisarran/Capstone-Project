import Checkbox from '@mui/material/Checkbox';
import FavoriteBorder from '@mui/icons-material/FavoriteBorderRounded';
import Favorite from '@mui/icons-material/FavoriteRounded';
import {useNavigate} from 'react-router-dom';
import {base_url} from '../api/api.js'

function FavoriteButton({recipe,favorites,setFavorites}){
    const navigate = useNavigate();

        //use for checkedbox
    const  isFavorite = favorites.some((favorite)=>favorite.recipe_id === recipe.id)
    const label = { slotProps: { input: { 'aria-label': isFavorite ? 'Remove from favorites' : 'Add to favorites' } } };
            
        const handleFavorites = async (kind,recipe_id,checked) => {

            const savedToken = localStorage.getItem("token");
            // logged out: go to login instead of a silent 401 -Arun
            if (!savedToken){ navigate("/login"); return; }

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
                icon={<FavoriteBorder sx={{color:"app.primary"}}/>}
                checkedIcon={<Favorite sx={{color:"app.primary"}} />}
                checked = {isFavorite} 
                onChange={(e)=>{
                    handleFavorites("favorite",recipe.id,e.target.checked);
                }}        
            />
        </>
    );
}

export default FavoriteButton;