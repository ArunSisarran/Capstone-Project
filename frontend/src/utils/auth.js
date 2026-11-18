import {base_url} from '../api/api.js'

export const SERVER_DOWN = "We can't reach the server right now. Try again in a minute.";

// 422 details are lists, not messages -Arun
export const errorText = (data, fallback) => typeof data?.detail === "string" ? data.detail : fallback;

export async function logInWith(email, password){
    const response = await fetch(`${base_url}/auth/login`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email, password}),
    });
    if (response.status === 401) throw new Error("That email and password don't match.");
    if (!response.ok) throw new Error(errorText(await response.json().catch(() => null), "Couldn't log in. Try again."));
    const {access_token} = await response.json();
    const me = await fetch(`${base_url}/users/me`, {headers: {Authorization: `Bearer ${access_token}`}});
    return {token: access_token, user: me.ok ? await me.json() : null};
}
