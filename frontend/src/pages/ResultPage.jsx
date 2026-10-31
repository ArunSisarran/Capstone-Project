import React, {useState,useEffect} from 'react'
import {useParams} from 'react-router-dom'
import {mockData} from '../mock/mockdata.js'
import Grid from '@mui/material/Grid';
import RecipeCard from '../components/RecipeCard'
import '../css/ResultPage.css'
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import TextField from '@mui/material/TextField';
import Chip from '@mui/material/Chip';
import Stack from '@mui/material/Stack';
import Divider from '@mui/material/Divider';

function ResultPage({history,setHistory,favorites,setFavorites,savedforlater,setSavedForLater,result,setResult}) {
    {/*Set Up Filters */}
    const [keyword, setKeyword] = useState("");
    const [allergyFood, setAllergyFood] = useState("none");

    //track the users options
    const [dietaryTag, setDietaryTag] = useState("");
    //if have more options

    const [cuisinePreference, setCuisinePreference] = useState("none");
    
   // const recipes = mockData.recommendations;

    const handleKeywordChange = (e) => setKeyword(e.target.value);
    const handleAllergyChange = (e) => setAllergyFood(e.target.value);


    const handleDietaryChange = (e) => setDietaryTag(e.target.value);
        

    const handleCuisinePreference = (e) => setCuisinePreference(e.target.value);

 //   const filteredControl = recipes.filter((recipe) => 
  //       recipe.dietaryTag.toLowerCase().includes(dietaryTag.toLowerCase())

        
    //);

        const handleClick = () => {
        console.info('You clicked the Chip.');
    };

    const ingredientsTag = mockData.ingredientData.detectedTags;


    useEffect(()=>{
        fetch("http://127.0.0.1:8000/recipes?skip=0&limit=20")
        .then((res)=>res.json())
        .then((json) => {
            setResult(json);
        });
    },[result])

    return(
        <>
        <div className="result">
            <div className="header">
                 Recipe Recommendation Generating...
            </div>

            <div className="result-section">            
                <div  className="filter-control"> 
                    <div className = "filter-title">Filter</div>
                        <div className="allergy-category"> Allergy:
                            <FormGroup>
                            <FormControlLabel control={<Checkbox defaultChecked sx={{minHeight:0,height:'10px' }} />} label="none" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} label= "Egg"/>
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} label="Milk" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} label="Peanut" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px'}}/>} label="Soy" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} label="Wheat" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} label="Tree nut" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} label="Shellfish" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px'}}/>} label="Fish" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} label="Seasame" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} label="Other allergies food"/>
                            <TextField />
                            </FormGroup>
                        </div>

                        <div className="dietary-category"> Dietary-Restriction:
                            <FormGroup>
                            <FormControlLabel control={<Checkbox  sx={{minHeight:0,height:'10px' }} />} label="none" onChange= {handleDietaryChange} value="none"/>
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} label="gluten-free" onChange= {handleDietaryChange} value="gluten-free" />
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} label="dairy-free" onChange= {handleDietaryChange}/>
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} label="vegatarianism" onChange= {handleDietaryChange}/>
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px'}}/>} label="vaganism" onChange= {handleDietaryChange}/>
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} label="lactose intolerance" onChange= {handleDietaryChange}/>
                            <FormControlLabel control={<Checkbox sx={{minHeight:0,height:'10px' }}/>} label="other"/>
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
                        <button className="filter-button">Apply filter </button>                       
                        <button className="filter-button">Reset filter </button>     
        
                </div>

                {/*Card-Section*/}
                <div className="card">  
                
                 <div className="ingredients-tags">
                
                <p>Ingredients Tags:  </p>
                <Stack direction="row" spacing={1}>
                {ingredientsTag.map((ingredient) => (
                <Chip 
                    label={ingredient.ingredient} 
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
                        {result.map((recipe) => (
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