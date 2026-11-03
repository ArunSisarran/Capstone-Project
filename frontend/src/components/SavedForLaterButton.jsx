import Checkbox from '@mui/material/Checkbox';
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorder';
import BookmarkIcon from '@mui/icons-material/Bookmark';

function FavoriteButton({recipe,savedforlater,setSavedForLater}){
    const label = { slotProps: { input: { 'aria-label': 'Checkbox demo' } } };

       const isSaved = savedforlater.some((s) => s.id === recipe.id);

        const newSaved = {
        id:recipe.id,
        title:recipe.title,
        viewedAt:new Date(). toISOString(),
    };
    const handleSaved = () =>{
         savedforlater = JSON.parse(localStorage.getItem("clickSaved") || "[]");

        const seen = savedforlater.some((item) => item.id === recipe.id);

        const addNewSaved = seen
            ? savedforlater.filter(item => item.id !== recipe.id)
            :[
                newSaved,
                ...savedforlater
            ];
        localStorage.setItem("clickSaved", JSON.stringify(addNewSaved));

        //console.log("later id:", addNewSaved);
        setSavedForLater(addNewSaved);
    };
 
    return (
        <>
                <Checkbox
                    {...label}
                    icon={<BookmarkBorderIcon sx={{color:"rgb(89,45,59)"}} />}
                    checkedIcon={<BookmarkIcon/>}
                    checked = {isSaved}
                    onChange={handleSaved}
                />

    </>
    );
}

export default FavoriteButton;