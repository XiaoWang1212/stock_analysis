<template>
  <div id="app">
    <header v-if="!$route.meta.hideHeader">
      <nav>
        <div class="nav-left">
          <router-link to="/home" class="icon-link">
            <span class="material-icons">account_circle</span>
          </router-link>
          <router-link to="/stock-heatmap">Stock Maps</router-link>
          <router-link to="/stock-app">Stock Analysis</router-link>
        </div>
      </nav>
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
    color: #2c3e50;
    min-height: 100vh;
    position: relative;
    background: #f5f5f7;
  }

  .stock-analysis {
    padding: var(--content-padding);
    max-width: var(--container-max-width);
    width: 100%;
    margin: 0 auto;
    box-sizing: border-box;
  }

  .icon-link {
    display: flex;
    align-items: center;
    padding: 8px;
  }

  .material-icons {
    font-size: 24px;
  }

  header {
    background-color: rgba(51, 51, 51, 0.9);
    padding: 10px;
    position: relative;
  }

  nav {
    display: flex;
    justify-content: flex-start;
    align-items: center;
  }

  .nav-left {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  nav a {
    color: white;
    text-decoration: none;
    padding: 10px;
    font-size: 16px;
    transition: background-color 0.3s, font-size 0.3s;
  }

  nav a:hover {
    background-color: #555;
    font-size: 18px;
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
