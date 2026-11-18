import Checkbox from '@mui/material/Checkbox';
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorderRounded';
import BookmarkIcon from '@mui/icons-material/BookmarkRounded';
import {useNavigate} from 'react-router-dom';
import {base_url} from '../api/api.js'

function FavoriteButton({recipe,savedforlater,setSavedForLater}){
    const navigate = useNavigate();

       const isSaved = savedforlater.some((saved) => saved.recipe_id === recipe.id);
    const label = { slotProps: { input: { 'aria-label': isSaved ? 'Remove from saved' : 'Save for later' } } };

       const handleSaved = async (kind,recipe_id,checked) => {

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
                setSavedForLater((prev) =>
                    prev.some((recipe)=>(recipe.recipe_id)===recipe_id)
                    ? prev
                    :[...prev, {recipe_id:recipe_id, recipe:recipe}]);
                } else {
                setSavedForLater((prev) =>
                    prev.filter((saved) => (saved.recipe_id) !== (recipe_id))
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
                    icon={<BookmarkBorderIcon sx={{color:"app.primary"}} />}
                    checkedIcon={<BookmarkIcon sx={{color:"app.primary"}}/>}
                    checked = {isSaved}
                    onChange={(e)=>{
                    handleSaved("saved",recipe.id,e.target.checked);
                }}
                />

    </>
    );
}

export default FavoriteButton;