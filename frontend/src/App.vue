<template>
  <div id="app">
    <header>
      <nav>
        <div class="nav-left">
          <router-link to="/">Home</router-link>
          <div class="dropdown">
            <button class="dropbtn">COVID-19 Analysis</button>
            <div class="dropdown-content">
              <router-link to="/birth-rate">Birth Rate</router-link>
              <router-link to="/death-rate">Death Rate</router-link>
              <router-link to="/economic-impact">Economic Impact</router-link>
            </div>
          </div>
          <router-link to="/stock-app">Stock Analysis</router-link>
        </div>
      </nav>
    </header>
    <router-view/>
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

header {
  background-color: #333;
  padding: 10px;
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
  box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
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