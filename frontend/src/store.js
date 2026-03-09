import { configureStore } from "@reduxjs/toolkit";
import { productListReducer } from "./reducers/productsReducers";
import { combineReducers } from "redux";

const reducer = combineReducers({
    productList: productListReducer,
});

const initialState = {};

const store = configureStore({
  reducer,
  preloadedState: initialState,
});

export default store;