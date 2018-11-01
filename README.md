Description:<br>
This application allows you to search Etsy for products and shops, returning the top 5 results for each search. It stores information about the top 5 results in a database every time someone searches. There are several view functions that allow you to browse through the saved data.

Routes:<br>
/etsy --> etsyform.html<br>
/etsy_results --> etsy_results.html<br>
/etsy/<search> --> etsy_results.html<br>
/search/shops --> shopform.html<br>
/all_shops --> all_shops.html<br>
/all_products --> all_products.html<br>
/all_users --> all_users.html<br>
/favorite --> favorite_product.html<br>

Checklist:<br>
**Ensure that the SI364midterm.py file has all the setup (app.config values, import statements, code to run the app if that file is run, etc) necessary to run the Flask application, and the application runs correctly on http://localhost:5000 (and the other routes you set up)**<br>
**Add navigation in base.html with links (using a href tags) that lead to every other viewable page in the application. (e.g. in the lecture examples from the Feb 9 lecture, like this )**<br>
**Ensure that all templates in the application inherit (using template inheritance, with extends) from base.html and include at least one additional block.**<br>
**Include at least 2 additional template .html files we did not provide.**<br>
**At least one additional template with a Jinja template for loop and at least one additional template with a Jinja template conditional.**<br>
**These could be in the same template, and could be 1 of the 2 additional template files.**<br>
**At least one errorhandler for a 404 error and a corresponding template.**<br>
**At least one request to a REST API that is based on data submitted in a WTForm.**<br>
**At least one additional (not provided) WTForm that sends data with a GET request to a new page.**<br>
**At least one additional (not provided) WTForm that sends data with a POST request to the same page.**<br>
**At least one custom validator for a field in a WTForm.**<br>
**At least 2 additional model classes.**<br>
**Have a one:many relationship that works properly built between 2 of your models.**<br>
**Successfully save data to each table.**<br>
**Successfully query data from each of your models (so query at least one column, or all data, from every database table you have a model for).**<br>
**Query data using an .all() method in at least one view function and send the results of that query to a template.**<br>
**Include at least one use of redirect. (HINT: This should probably happen in the view function where data is posted...)**<br>
**Include at least one use of url_for. (HINT: This could happen where you render a form...)**<br>
**Have at least 3 view functions that are not included with the code we have provided. (But you may have more! Make sure you include ALL view functions in the app in the documentation and ALL pages in the app in the navigation links of base.html.)**<br><br>
**(100 points) Include an additional model class (to make at least 4 total in the application) with at least 3 columns. Save data to it AND query data from it; use the data you query in a view-function, and as a result of querying that data, something should show up in a view. (The data itself should show up, OR the result of a request made with the data should show up.)**<br>
**(100 points) Write code in your Python file that will allow a user to submit duplicate data to a form, but will not save duplicate data (like the same user should not be able to submit the exact same tweet text for HW3).**<br>
