import React, {useState,useEffect} from 'react'
import {useParams} from 'react-router-dom'
import RecipeCard from '../components/RecipeCard'
import '../css/ResultPage.css'
import Grid from '@mui/material/Grid';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import TextField from '@mui/material/TextField';
import Chip from '@mui/material/Chip';
import Stack from '@mui/material/Stack';
import Divider from '@mui/material/Divider';

function ResultPage({history,setHistory,favorites,setFavorites,savedforlater,setSavedForLater,result,setResult}) {
        // use for render api
    const [dietaryTag, setDietaryTag] = useState([]);


    {/*Set Up Filters */}
    const [keyword, setKeyword] = useState("");//not for keyword yet
    const [allergyFood, setAllergyFood] = useState("none");

    //keep it for temp; not sure for cuisine preference
    const [cuisinePreference, setCuisinePreference] = useState("none");
    const handleCuisinePreference = (e) => setCuisinePreference(e.target.value);

    //when the user is choosing
    const[filters, setFilters]= useState({AllergyFood:"None",DietaryTag:"None"});

    //after the user finished, and click apply
    const [appliedFilters, setAppliedFilters] =  useState({AllergyFood:"None",DietaryTag:"None"});
 

    const handleClick = () => {
        console.info('You clicked the Chip.');
    };


    //render ingredients from api
    const [ingredientsTag,setIngredientsTag] = useState([])


    //Get the list of recipes, list of dietray-tag, and the list of ingredients JSON data from api
    useEffect(()=>{
        fetch("http://127.0.0.1:8000/recipes?skip=0&limit=20")
        .then((res)=>res.json())
        .then((json) => {
            setResult(json);
        });
    },[result])

        useEffect(()=>{
        fetch("http://127.0.0.1:8000/dietary-tags")
        .then((res)=>res.json())
        .then((json) => {
            setDietaryTag(json);
        });
    },[dietaryTag])

    useEffect(()=>{
        fetch("http://127.0.0.1:8000/ingredients")
        .then((res)=>res.json())
        .then((json)=>{
            setIngredientsTag(json);
        });
    },[ingredientsTag])

    const handleApplyFilter = () =>{
        console.log("before apply:", appliedFilters)
        console.log("after apply:",filters)

        setAppliedFilters({...filters});
    };

    const handleResetFilter = ()=>{
        setFilters({AllergyFood:"None",DietaryTag:"None"});
        setAppliedFilters({AllergyFood:"None",DietaryTag:"None"});
    }

     const filteredControl = result.filter((recipe) => {
       const matchedAllergyFood =
        appliedFilters.AllergyFood === "None" ||
        !recipe.ingredients.some((ingredient)=>(ingredient.name === appliedFilters.AllergyFood))

        const matchedDietaryTag = 
        appliedFilters.DietaryTag === "None" ||
        recipe.dietary_tags.some((dietaryTag)=>(dietaryTag.name === appliedFilters.DietaryTag))

        return matchedAllergyFood && matchedDietaryTag
        
    });

    return(
        <>
        <div className="result">
            <div className="header">
                 Recipe Recommendation Generating...
            </div>

            <div className="result-section">            
                <div  className="filter-control"> 
                    <div className = "filter-title">Filter</div>
                        <div className="allergy-category"> Allergy Food:
                            <FormGroup value = {filters.AllergyFood} onChange={(e) => setFilters({...filters,AllergyFood:e.target.value})}>
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} value ="egg" label= "egg"/>
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} value="milk" label="milk" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} value = "peanut "label="peanut" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px'}}/>} value = "soy" label="soy" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} value = "wheat" label="wheat" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} value = "tree nut" label="tree nut" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} value = "shellfish" label="shellfish" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px'}}/>} value = "fish" label="fish" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} value = "seasame" label="seasame" />
                            <TextField />
                            </FormGroup>
                        </div>

                        <div className="dietary-category"> Dietary-Restriction:
                            <FormGroup value = {filters.DietaryTag} onChange={(e) => setFilters({...filters,DietaryTag:e.target.value})}>
                                {dietaryTag.map((dietary)=>(
                                 <FormControlLabel control={<Checkbox  sx={{minHeight:0,height:'10px' }} />} key={dietary.id} value= {dietary.name} label = {dietary.name}/>
                                ))

                                }

                            <TextField />
                            </FormGroup>
                        </div> 

                        <div className="cuisine-category"> Cuisine Preference:
                            <FormGroup>
                            <FormControlLabel control={<Checkbox defaultChecked sx={{minHeight:0,height:'10px' }} />} label="none" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} label="American" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} label="Italian" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} label="Mexican" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px'}}/>} label="Chinese" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} label="other"/>
                            <TextField />
                            </FormGroup>
                        </div>                       
                        <button className="filter-button" onClick = {handleApplyFilter}>Apply filter </button>                       
                        <button className="filter-button" onClick = {handleResetFilter}>Reset filter </button>     
        
                </div>

                {/*Card-Section*/}
                <div className="card">  
                
                 <div className="ingredients-tags">
                
                <p>Ingredients Tags:  </p>
                <Stack direction="row" spacing={1}>
                {ingredientsTag.map((ingredient) => (
                <Chip 
                    label={ingredient.name} 
                    key ={ingredient.id} 
                    variant="outlined" 
                    onClick={handleClick} 

                    sx = {{color:'rgb(89,54,45)', border: '1px solid rgb(89,54,45)'}}
                
                />
                        ))}
                </Stack>
            </div>   

            <Divider sx={{backgroundColor:"rgb(89,54,45)"}} />

                    <Grid container spacing = {3} sx ={{p:3, width:"100%", boxSizing:"border-box"}}>
                        {filteredControl.map((recipe) => (
                            <Grid recipe size={4} key={recipe.id}>
                                <RecipeCard 
                                    recipe={recipe} 
                                    history = {history}
                                    setHistory = {setHistory}
                                    favorites = {favorites} 
                                    setFavorites = {setFavorites}
                                    savedforlater = {savedforlater}
                                    setSavedForLater = {setSavedForLater}
                                />
                            </Grid>
                        ))}
                    </Grid>
                
                </div>
            </div>
            </div>
        </>
    );
}

export default ResultPage;