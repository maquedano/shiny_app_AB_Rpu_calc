# Revenue per Visitor Statistical Significance Calculator

Trying to understand the underlying statistics, I developed this RPU A/B test calculator (with frequentist calculations) based upon an existing calculator that I have been using in my CRO work by [BLAST](https://www.blastanalytics.com/rpv-calculator); 
But in this case I created the calculator as a Shiny app with Python, they did with R (RStudio IDE -> Posit). R is great for statistical calculations, and Shiny for R is way more robust and mature than the new version for Python that was just released last year. But... I've just enjoy more coding with Python than R, sorry 😅
Documentation is not that super great, but got there in the end. Other frameworks in Python are also great like streamlit, but I  Shiny offers free hosting and also is well known in data science.

* APP deployed on → https://maquedano.shinyapps.io/rpu-ab-test-calc/

### For deploying the Shiny app
* For deploying the app I followed the [deployment instructions](https://shiny.posit.co/py/docs/deploy-cloud.html)  on their web. 
* Basically create an account on [shinyapps.io](https://www.shinyapps.io/), which offers hosting up to 5 apps per user for free
* Get your token from the account (Account > Tokens > Add Token > Show > With Python > Copy to clipboard)
* run in your app folder the followig command in a terminal to initialize the connections and credentials with shinyapps.io. Example of what I run:
`rsconnect add --account maquedano --name maquedano --token XXXXXXXXXX`
* Deploy the app with the following command (with your own name of your account), example of what I run:
`rsconnect deploy shiny . --name maquedano --title RPU-AB-test-calc`