<template>
  <div id="app">
    <header v-if="!$route.meta.hideHeader">
      <nav>
        <div class="nav-left">
          <router-link to="/stock-heatmap">股票行情</router-link>
          <router-link to="/tw-stock-categories"> 台股分類 </router-link>
          <router-link to="/stock-app">股票分析</router-link>
        </div>
      </nav>
      <router-link to="/home" class="icon-link">
        <span class="material-icons">account_circle</span>
      </router-link>
    </header>
    <router-view />
  </div>
</template>

:root { --container-max-width: 1200px; --content-padding: 30px; }

<style>
  #app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: white;
    min-height: 100vh;
    position: relative;
    background: #272727;
  }

  header{
    display: flex;
    justify-content: space-between;
  }

  .stock-analysis {
    padding: var(--content-padding);
    max-width: var(--container-max-width);
    margin: 0 auto;
    box-sizing: border-box;
  }

  .icon-link {
    margin-right: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    text-decoration: none;
  }

  .material-icons {
    color: white;
    font-size: 30px; 
    transition: transform 0.3s ease-in-out; 
  }

  .material-icons:hover{
    color: #84C1FF;
    transform: scale(1.5);
  }

  header {
    background-color: #5B5B5B;
    box-shadow : 0px 0px 5px 3px #D0D0D0;
    padding: 10px;
    position: relative;
  }

  nav {
    padding-left: 20px;
    display: flex;
    justify-content: flex-start;
    align-items: center;
  }

  .nav-left {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
  }

  nav a {
    color: white;
    text-decoration: none;
    padding: 10px;
    font-size: 16px;
    font-weight: bold;
    border-radius: 20px;
    transition: background-color 0.3s, font-size 0.3s;
  }

  nav a:hover {
    background-color: #66B3FF;
    color: white;
    border-radius: 20px;
    font-size: 18px;
  }

  .router-link-active{
    border-radius: 20px;
    background-color: #66B3FF;
    color: white;
  }

  .dropdown {
    position: relative;
    display: inline-block;
  }

  .dropbtn {
    background-color: #333;
    color: white;
    padding: 10px;
    border: none;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s, font-size 0.3s;
  }

  .dropbtn:hover {
    background-color: #555;
    font-size: 18px;
  }

  .dropdown-content {
    display: none;
    position: absolute;
    background-color: #f9f9f9;
    min-width: 160px;
    box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.2);
    z-index: 1;
  }

  .dropdown-content a {
    color: black;
    padding: 12px 16px;
    text-decoration: none;
    display: block;
    transition: background-color 0.3s, font-size 0.3s;
  }

  .dropdown-content a:hover {
    background-color: #ddd;
    font-size: 18px;
  }

  .dropdown:hover .dropdown-content {
    display: block;
  }

  .dropdown:hover .dropbtn {
    background-color: #555;
  }
</style>
