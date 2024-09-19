<a id="config"></a>

# config

<a id="config.save_data"></a>

#### save\_data

```python
def save_data(data) -> bool
```

Save login data to the config.yaml file.

**Arguments**:

- `data` _dict_ - The login data to be saved.

<a id="config.get_config_path"></a>

#### get\_config\_path

```python
def get_config_path() -> str
```

Get the path to the config.yaml file.

**Returns**:

- `str` - The absolute path to the config.yaml file.

<a id="config.write_to_yaml"></a>

#### write\_to\_yaml

```python
def write_to_yaml(file_path, data) -> bool
```

Write data to a YAML file.

**Arguments**:

- `file_path` _str_ - The path to the YAML file.
- `data` _dict_ - The data to be written to the file.
  

**Returns**:

- `bool` - The sucess.

<a id="config.settings_loader"></a>

# config.settings\_loader

<a id="config.settings_loader.load_settings"></a>

#### load\_settings

```python
def load_settings(config_file: str = os.path.join(os.path.dirname(__file__),
                                                  "config.yaml")) -> dict
```

Load YAML configuration from the given file.

**Arguments**:

- `config_file`: Path to the YAML configuration file

**Returns**:

Dictionary containing the loaded settings

<a id="logs"></a>

# logs

<a id="logs.log"></a>

# logs.log

<a id="logs.log.Logger"></a>

## Logger Objects

```python
class Logger()
```

A class to handle logging with different log types.

**Attributes**:

- `LOG_DIR` _str_ - The directory where log files will be stored.
- `GENERAL_LOG_FILE` _str_ - Base filename for general log files.
- `RETURN_LOG_FILE` _str_ - Base filename for return log files.
- `LOG_FILE_EXTENSION` _str_ - The extension for log files.

<a id="logs.log.Logger.__init__"></a>

#### \_\_init\_\_

```python
def __init__(log_type: Literal["general", "return"] = "general")
```

Initialize the Logger with a specific log type.

**Arguments**:

- `log_type` _str_ - The type of the log, either 'general' or 'return'.

<a id="src"></a>

# src

<a id="src.main"></a>

# src.main

<a id="src.main.initialize_application"></a>

#### initialize\_application

```python
def initialize_application() -> Scraper
```

Initialize the application by setting up the login window and scraper.

**Returns**:

- `Scraper` - An instance of the Scraper class with an initialized WebDriver.

<a id="src.main.execute_scraping"></a>

#### execute\_scraping

```python
def execute_scraping(scraper: Scraper)
```

Execute the table scraping process and return the scraped DataFrame.

**Arguments**:

- `scraper` _Scraper_ - An instance of the Scraper class.
  

**Returns**:

- `DataFrame` - The DataFrame obtained from the scraping process.

<a id="src.main.get_page_id_from_code"></a>

#### get\_page\_id\_from\_code

```python
def get_page_id_from_code(df, notion_factory: NotionRequestFactory) -> dict
```

Given a DataFrame with 'CÓDIGO' column, search for the corresponding page in Notion.

**Arguments**:

- `df` _DataFrame_ - The DataFrame containing the 'CÓDIGO' column.
- `notion_factory` _NotionRequestFactory_ - An instance of the NotionRequestFactory.
  

**Returns**:

- `dict` - A dictionary mapping each code from the DataFrame to its corresponding page IDs in Notion.

<a id="src.main.create_notion_factories"></a>

#### create\_notion\_factories

```python
def create_notion_factories() -> dict[str, NotionRequestFactory]
```

Creates and returns NotionRequestFactory instances for different Notion databases.

**Returns**:

  dict[str, NotionRequestFactory]: A dictionary with NotionRequestFactory instances for each database type.

<a id="src.main.generate_page_code_maps"></a>

#### generate\_page\_code\_maps

```python
def generate_page_code_maps(
    df: pd.DataFrame, notion_factories: dict[str, NotionRequestFactory]
) -> dict[str, dict[str, Union[str, list[str]]]]
```

Generates page code maps for each Notion database based on the DataFrame.

**Arguments**:

- `df` _pd.DataFrame_ - The DataFrame containing the data.
- `notion_factories` _dict[str, NotionRequestFactory]_ - A dictionary with NotionRequestFactory instances.
  

**Returns**:

  dict[str, dict[str, Union[str, list[str]]]]: A dictionary with page code maps for each Notion database.

<a id="src.main.update_all_notion_tables"></a>

#### update\_all\_notion\_tables

```python
def update_all_notion_tables(df: pd.DataFrame,
                             page_code_maps: dict[str, dict[str,
                                                            Union[str,
                                                                  list[str]]]],
                             notion_factories: dict[str,
                                                    NotionRequestFactory])
```

Updates all Notion tables with data from the DataFrame.

**Arguments**:

- `df` _pd.DataFrame_ - The DataFrame containing the data.
- `page_code_maps` _dict[str, dict[str, Union[str, list[str]]]]_ - A dictionary with page code maps for each Notion database.
- `notion_factories` _dict[str, NotionRequestFactory]_ - A dictionary with NotionRequestFactory instances.

<a id="src.main.main"></a>

#### main

```python
def main()
```

Main entry point for the SIAC Scraping project.
Initializes the application, performs scraping, and updates Notion databases.

<a id="src.main_window"></a>

# src.main\_window

<a id="src.main_window.MainWindow"></a>

## MainWindow Objects

```python
class MainWindow(GenericWindow)
```

A class to create a combined window with two tabs: one for login functionality and one for Notion login.

<a id="src.main_window.MainWindow.__init__"></a>

#### \_\_init\_\_

```python
def __init__() -> None
```

Initialize the CombinedWindow class and set up the UI.

<a id="src.main_window.MainWindow.get_driver"></a>

#### get\_driver

```python
def get_driver() -> Optional[webdriver.Chrome]
```

Return the Selenium WebDriver instance.

**Returns**:

- `Optional[webdriver.Chrome]` - An instance of Selenium WebDriver.

<a id="src.notion_update"></a>

# src.notion\_update

<a id="src.notion_update.update_notion"></a>

#### update\_notion

```python
def update_notion(df: pd.DataFrame,
                  page_code_map: dict[str, Union[str, list[str]]],
                  notion_factory: NotionRequestFactory,
                  table_type: str = "main")
```

Main function to update Notion pages based on the table type.

**Arguments**:

- `df` _DataFrame_ - The DataFrame containing the data to update.
- `page_code_map` _dict_ - A dictionary mapping codes to Notion page IDs or lists of page IDs.
- `notion_factory` _NotionRequestFactory_ - An instance of the NotionRequestFactory.
- `table_type` _str_ - The type of table to update ("main", "rr", "timeline").

<a id="src.notion_update.update_main_notion"></a>

#### update\_main\_notion

```python
def update_main_notion(df: pd.DataFrame,
                       page_code_map: dict[str, Union[str, list[str]]],
                       notion_factory: NotionRequestFactory)
```

Updates Notion pages with the corresponding data from the DataFrame.

**Arguments**:

- `df` _DataFrame_ - The DataFrame containing the data to update.
- `page_code_map` _dict_ - A dictionary mapping codes to Notion page IDs or lists of page IDs.
- `notion_factory` _NotionRequestFactory_ - An instance of the NotionRequestFactory.

<a id="src.notion_update.update_rr_notion"></a>

#### update\_rr\_notion

```python
def update_rr_notion(df: pd.DataFrame,
                     page_code_map: dict[str, Union[str, list[str]]],
                     notion_factory: NotionRequestFactory)
```

Verifies if all rows with RES = 'RR' are present in the Notion table. Creates or updates pages accordingly.

**Arguments**:

- `df` _DataFrame_ - The DataFrame containing the data to update.
- `page_code_map` _dict_ - A dictionary mapping codes to Notion page IDs or lists of page IDs.
- `notion_factory` _NotionRequestFactory_ - An instance of the NotionRequestFactory.

<a id="src.notion_update.update_timeline_notion"></a>

#### update\_timeline\_notion

```python
def update_timeline_notion(df: pd.DataFrame,
                           page_code_map: dict[str, Union[str, list[str]]],
                           notion_factory: NotionRequestFactory)
```

Updates Notion pages for the timeline table by processing each period in the given DataFrame.
For each period, the function creates or updates pages in Notion based on the provided mapping and factory.

**Arguments**:

- `df` _pd.DataFrame_ - DataFrame containing data with columns 'PERÍODO', 'CÓDIGO', 'MATÉRIA', 'CH', and 'NOTA'.
- `page_code_map` _dict[str, Union[str, list[str]]]_ - Dictionary mapping periods to Notion page IDs or lists of page IDs.
- `notion_factory` _NotionRequestFactory_ - Instance of NotionRequestFactory used to interact with Notion API.

<a id="src.notion_update.create_new_period_page"></a>

#### create\_new\_period\_page

```python
def create_new_period_page(period: str, semester: int,
                           notion_factory: NotionRequestFactory) -> str
```

Creates a new page for the specified period and returns the page ID if successful.

**Arguments**:

- `period` _str_ - The period name.
- `semester` _int_ - The current semester number.
- `notion_factory` _NotionRequestFactory_ - An instance of the NotionRequestFactory.
  

**Returns**:

- `Optional[str]` - The newly created page ID, or None if creation failed.

<a id="src.notion_update.process_period"></a>

#### process\_period

```python
def process_period(period: str, group: pd.DataFrame, semester: int,
                   page_code_map: dict[str, Union[str, list[str]]],
                   notion_factory: NotionRequestFactory)
```

Handles the creation or update of Notion pages for a given period. If a page for the period does not exist,
it creates a new page and updates the mapping accordingly.

**Arguments**:

- `period` _str_ - The period to process.
- `group` _pd.DataFrame_ - DataFrame containing rows for the given period.
- `semester` _int_ - The semester number associated with the period.
- `page_code_map` _dict[str, Union[str, list[str]]]_ - Dictionary mapping periods to Notion page IDs or lists of page IDs.
- `notion_factory` _NotionRequestFactory_ - Instance of NotionRequestFactory used to interact with Notion API.

<a id="src.notion_update.handle_missing_period_page"></a>

#### handle\_missing\_period\_page

```python
def handle_missing_period_page(period: str, semester: int,
                               notion_factory: NotionRequestFactory,
                               page_code_map: dict[str, Union[str,
                                                              list[str]]])
```

Handles the situation where a Notion page for a given period does not exist. Creates a new page and updates
the page_code_map with the new page ID.

**Arguments**:

- `period` _str_ - The period for which a new page needs to be created.
- `semester` _int_ - The semester number associated with the period.
- `notion_factory` _NotionRequestFactory_ - Instance of NotionRequestFactory used to interact with Notion API.
- `page_code_map` _dict[str, Union[str, list[str]]]_ - Dictionary mapping periods to Notion page IDs or lists of page IDs.
  

**Returns**:

- `str` - The page ID of the newly created Notion page, or None if creation failed.

<a id="src.notion_update.process_row"></a>

#### process\_row

```python
def process_row(row: pd.Series, period_page_id: str,
                page_code_map: dict[str, Union[str, list[str]]],
                notion_factory: NotionRequestFactory)
```

Updates or creates a Notion page for a given row of data. The data includes code, subject, workload, and grade.

**Arguments**:

- `row` _pd.Series_ - Row data containing 'CÓDIGO', 'MATÉRIA', 'CH', and 'NOTA'.
- `period_page_id` _str_ - The ID of the Notion page related to the period.
- `page_code_map` _dict[str, Union[str, list[str]]]_ - Dictionary mapping codes to Notion page IDs or lists of page IDs.
- `notion_factory` _NotionRequestFactory_ - Instance of NotionRequestFactory used to interact with Notion API.

<a id="src.notion_update.build_notion_data"></a>

#### build\_notion\_data

```python
def build_notion_data(row: pd.Series, period_page_id: str) -> dict
```

Constructs the data payload for updating or creating a Notion page based on the provided row data.

**Arguments**:

- `row` _pd.Series_ - Row data containing 'CÓDIGO', 'MATÉRIA', 'CH', and 'NOTA'.
- `period_page_id` _str_ - The ID of the Notion page related to the period.
  

**Returns**:

- `dict` - The data payload for Notion API requests.

<a id="src.notion_update.process_code_page"></a>

#### process\_code\_page

```python
def process_code_page(code: str, page_code_map: dict[str, any], row: dict[str,
                                                                          any],
                      notion_factory: NotionRequestFactory,
                      data: dict[str, any]) -> None
```

Processes the given code to either update an existing page or create a new one in Notion.

If the code is found in `page_code_map`, the function updates the corresponding pages.
If the code is not found, a new page is created in Notion with the provided `data`.

**Arguments**:

- `code` _str_ - The unique code representing the page.
- `page_code_map` _dict[str, Any]_ - A mapping of codes to Notion page IDs.
- `row` _dict[str, Any]_ - A dictionary containing row data with the 'NOTA' field.
- `notion_factory` _NotionRequestFactory_ - An instance of NotionRequestFactory to handle Notion API requests.
- `data` _dict[str, Any]_ - The data to be used when creating a new page in Notion.
  

**Returns**:

  None

<a id="src.notion_update.get_filtered_rows"></a>

#### get\_filtered\_rows

```python
def get_filtered_rows(df: pd.DataFrame, column_name: str,
                      code: str) -> pd.DataFrame
```

Filters the DataFrame for rows matching the given code in the specified column.

**Arguments**:

- `df` _DataFrame_ - The DataFrame to filter.
- `column_name` _str_ - The name of the column to match the code.
- `code` _str_ - The code to match in the DataFrame.
  

**Returns**:

- `DataFrame` - Filtered rows matching the code in the specified column.

<a id="src.notion_update.sort_rows_by_priority"></a>

#### sort\_rows\_by\_priority

```python
def sort_rows_by_priority(
        filtered_rows: pd.DataFrame,
        res_priority: list[str] = ["AP", "DU", "DI", "RR"]) -> pd.DataFrame
```

Sorts the filtered rows by 'RES' priority and 'NOTA'.

**Arguments**:

- `filtered_rows` _DataFrame_ - The filtered rows to be sorted.
- `res_priority` _list_ - A list defining the priority order for the 'RES' column. Default is ["AP", "DU", "DI", "RR"].
  

**Returns**:

- `DataFrame` - Sorted rows based on 'RES' priority and 'NOTA'.

<a id="src.notion_update.ensure_page_ids_is_list"></a>

#### ensure\_page\_ids\_is\_list

```python
def ensure_page_ids_is_list(page_ids: Union[str, list[str]]) -> list[str]
```

Ensures that page_ids is always a list.

**Arguments**:

- `page_ids` - The page ID or list of page IDs.
  

**Returns**:

- `list` - A list of page IDs.

<a id="src.notion_update.update_pages_with_rows"></a>

#### update\_pages\_with\_rows

```python
def update_pages_with_rows(sorted_rows: pd.DataFrame, page_ids: list[str],
                           code: str, notion_factory: NotionRequestFactory)
```

Updates the Notion pages with the corresponding rows of data from the DataFrame.

**Arguments**:

- `sorted_rows` _DataFrame_ - The sorted rows to update.
- `page_ids` _list_ - The list of page IDs to update.
- `code` _str_ - The code corresponding to the page and rows.
- `notion_factory` _NotionRequestFactory_ - An instance of the NotionRequestFactory.

<a id="src.notion_update.log_and_update_page"></a>

#### log\_and\_update\_page

```python
def log_and_update_page(page_id: str, code: str, row: pd.Series,
                        notion_factory: NotionRequestFactory)
```

Logs the update and performs the actual update of the Notion page.

**Arguments**:

- `page_id` _str_ - The Notion page ID to update.
- `code` _str_ - The code corresponding to the page and row.
- `row` _pd.Series_ - The row of data to update in the Notion page.
- `notion_factory` _NotionRequestFactory_ - An instance of the NotionRequestFactory.

<a id="src.scraper"></a>

# src.scraper

<a id="src.scraper.TableDataFilter"></a>

## TableDataFilter Objects

```python
class TableDataFilter()
```

A class to filter unwanted rows from table data.

<a id="src.scraper.TableDataFilter.filter_rows"></a>

#### filter\_rows

```python
def filter_rows(data: List[List[str]]) -> List[List[str]]
```

Filter out unwanted rows from the table data.

**Arguments**:

- `data` _List[List[str]]_ - The table data to be filtered.
  

**Returns**:

- `List[List[str]]` - The filtered table data.

<a id="src.scraper.Scraper"></a>

## Scraper Objects

```python
class Scraper()
```

A class to handle scraping operations and convert table data to a Pandas DataFrame.

<a id="src.scraper.Scraper.__init__"></a>

#### \_\_init\_\_

```python
def __init__(driver)
```

Initialize the Scraper class with a Selenium WebDriver instance.

**Arguments**:

- `driver` - Selenium WebDriver instance.

<a id="src.scraper.Scraper.scrape_table"></a>

#### scrape\_table

```python
def scrape_table() -> pd.DataFrame
```

Perform scraping and convert the table data to a Pandas DataFrame.

**Returns**:

- `pd.DataFrame` - DataFrame containing the scraped and filtered data.

<a id="src.services.notion_api"></a>

# src.services.notion\_api

<a id="src.services.notion_api.NotionAdapter"></a>

## NotionAdapter Objects

```python
class NotionAdapter()
```

Adapter class to fetch Notion API configuration details.

<a id="src.services.notion_api.NotionAdapter.get_headers"></a>

#### get\_headers

```python
def get_headers() -> Dict[str, str]
```

Return the headers required for Notion API requests.

<a id="src.services.notion_api.NotionAdapter.get_base_url"></a>

#### get\_base\_url

```python
def get_base_url() -> str
```

Return the Notion base URL.

<a id="src.services.notion_api.NotionRequestFactory"></a>

## NotionRequestFactory Objects

```python
class NotionRequestFactory()
```

Factory class to create Notion API requests.

<a id="src.services.notion_api.NotionRequestFactory.create_page"></a>

#### create\_page

```python
def create_page(data: Dict[str, Any]) -> requests.Response
```

Create a new page in the Notion database.

**Arguments**:

- `data` _dict_ - The page properties.
  

**Returns**:

- `Response` - The response from the Notion API.

<a id="src.services.notion_api.NotionRequestFactory.get_pages"></a>

#### get\_pages

```python
def get_pages(num_pages: Optional[int] = None) -> List[Dict[str, Any]]
```

Retrieve pages from the Notion database.

**Arguments**:

- `num_pages` _Optional[int]_ - The number of pages to fetch. If None, fetch all.
  

**Returns**:

- `List[Dict]` - The list of pages.

<a id="src.services.notion_api.NotionRequestFactory.update_page"></a>

#### update\_page

```python
def update_page(page_id: str, data: Dict[str, Any]) -> requests.Response
```

Update a page in the Notion database.

**Arguments**:

- `page_id` _str_ - The ID of the page to update.
- `data` _dict_ - The properties to update.
  

**Returns**:

- `Response` - The response from the Notion API.

<a id="src.services"></a>

# src.services

<a id="src.utils.generic_window"></a>

# src.utils.generic\_window

<a id="src.utils.generic_window.GenericWindow"></a>

## GenericWindow Objects

```python
class GenericWindow()
```

A class to create a customizable window with tabbed interface using CustomTkinter.

**Attributes**:

- `title` _str_ - The title of the window.
- `tab_titles` _list[str]_ - Titles for each tab.
- `fields` _dict[str, list[str]]_ - A dictionary where keys are tab titles and values are lists of field labels for each tab.
- `button_texts` _dict[str, list[str]]_ - A dictionary where keys are tab titles and values are lists of button texts for each tab.
- `button_actions` _dict[str, list[Callable[[], None]]]_ - A dictionary where keys are tab titles and values are lists of button actions for each tab.
- `resizable` _bool_ - Whether the window is resizable.

<a id="src.utils.generic_window.GenericWindow.__init__"></a>

#### \_\_init\_\_

```python
def __init__(title: str,
             tab_titles: list[str],
             fields: dict[str, list[str]],
             button_texts: dict[str, list[str]],
             button_actions: dict[str, list[Callable[[], None]]],
             toggle_window: int,
             resizable: bool = True) -> None
```

Initialize the GenericWindow instance and configure the UI with tab view.

**Arguments**:

- `title` _str_ - The title of the window.
- `tab_titles` _list[str]_ - Titles for each tab.
- `fields` _dict[str, list[str]]_ - Field labels organized by tab title.
- `button_texts` _dict[str, list[str]]_ - Button texts organized by tab title.
- `button_actions` _dict[str, list[Callable[[], None]]]_ - Button actions organized by tab title.
- `toggle_window(int)` - Trigger the window resize event.
- `resizable` _bool_ - Whether the window is resizable.

<a id="src.utils.generic_window.GenericWindow.run"></a>

#### run

```python
def run() -> None
```

Start the CustomTkinter main loop.

<a id="src.utils"></a>

# src.utils

