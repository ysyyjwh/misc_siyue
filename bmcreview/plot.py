import os

# change into lib directory to load plot python scripts
main_path = os.getcwd()
lib_path = '/COVID19-Literature-Clustering-master/lib'
os.chdir(main_path + lib_path)

#from call_backs import input_callback, selected_code  # file with customJS callbacks for bokeh
                                                      # github.com/MaksimEkin/COVID19-Literature-Clustering/blob/master/lib/call_backs.py
import bokeh
from bokeh.models import ColumnDataSource, HoverTool, LinearColorMapper, CustomJS, Slider, TapTool, TextInput
#from bokeh.models.widgets.sliders import Slider
from bokeh.palettes import Category20
from bokeh.transform import linear_cmap, transform
from bokeh.io import output_file, show, output_notebook
from bokeh.plotting import figure
from bokeh.models import RadioButtonGroup, TextInput, Div, Paragraph
from bokeh.layouts import column, widgetbox, row, layout
from bokeh.layouts import column

import pandas 


# go back
os.chdir(main_path)

topic_path = 'data/topics.txt'
with open(topic_path) as f:
    topics = f.readlines()

y_pred = pandas.read_pickle('data/y_pred.p')
df = pandas.read_pickle('data/df_keywords.p')
X_embedded = pandas.read_pickle('data/X_embedded.p')


from bokeh.models.callbacks import CustomJS

# handle the currently selected article
def selected_code():
    code = """
            var titles = [];
            var authors = [];
            var journals = [];
            var years = [];
            cb_data.source.selected.indices.forEach(index => titles.push(source.data['titles'][index]));
            cb_data.source.selected.indices.forEach(index => authors.push(source.data['authors'][index]));
            cb_data.source.selected.indices.forEach(index => journals.push(source.data['journal'][index]));
            title = "<h4>" + titles[0].toString().replace(/<br>/g, ' ') + "</h4>";
            year = "<b>Journal</b>" + years[0].toString() + "<br>"
            authors = "<p1><b>Authors:</b> " + authors[0].toString().replace(/<br>/g, ' ') + "<br>"
            journal = "<b>Journal</b>" + journals[0].toString() + "<br>"
            current_selection.text = title + authors 
            current_selection.change.emit();
    """
    return code

# handle the keywords and search
def input_callback(plot, source, out_text, topics): 

    # slider call back for cluster selection
    callback = CustomJS(args=dict(p=plot, source=source, out_text=out_text, topics=topics), code="""
				var key = text.value;
				key = key.toLowerCase();
				var cluster = slider.value;
                var data = source.data; 
                              
                var x = data['x'];
                var y = data['y'];
                var x_backup = data['x_backup'];
                var y_backup = data['y_backup'];
                var labels = data['desc'];
                var abstract = data['abstract'];
                var titles = data['titles'];
                var authors = data['authors'];
                var journal = data['journal'];
                

                if (cluster == 15) {
                    out_text.text = 'Keywords: Slide to specific cluster to see the keywords.';
                    for (var i = 0; i < x.length; i++) {
						if(abstract[i].includes(key) || 
						titles[i].includes(key) || 
						authors[i].includes(key) || 
						journal[i].includes(key)) {
							x[i] = x_backup[i];
							y[i] = y_backup[i];
						} else {
							x[i] = undefined;
							y[i] = undefined;
						}
                    }
                }
                else {
                    out_text.text = 'Keywords: ' + topics[Number(cluster)];
                    for (var i = 0; i < x.length; i++) {
                        if(labels[i] == cluster) {
							if(abstract[i].includes(key) || 
							titles[i].includes(key) || 
							authors[i].includes(key) || 
							journal[i].includes(key)) {
								x[i] = x_backup[i];
								y[i] = y_backup[i];
							} else {
								x[i] = undefined;
								y[i] = undefined;
							}
                        } else {
                            x[i] = undefined;
                            y[i] = undefined;
                        }
                    }
                }
            source.change.emit();
            """)
    return callback


# show on notebook
output_notebook()
# target labels
y_labels = y_pred

# data sources
source = ColumnDataSource(data=dict(
    x = X_embedded[:,0], 
    y = X_embedded[:,1],
    x_backup = X_embedded[:,0],
    y_backup = X_embedded[:,1],
    desc= y_labels, 
    titles= df['Title'],
    authors = df['Authors'],
    journal = df['Journal/Book'],
    abstract = df['abstract'],
    labels = ["C-" + str(x) for x in y_labels],
    year = df['Publication Year']
    ))

# hover over information
hover = HoverTool(tooltips=[
    ("Title", "@titles{safe}"),
    ("Author(s)", "@authors{safe}"),
    ("Journal", "@journal{safe}"),
    ("Abstract", "@abstract{safe}"),
    ("Year", "@year{safe}"),
],
point_policy="follow_mouse")

# map colors
mapper = linear_cmap(field_name='desc', 
                     palette=Category20[15],
                     low=min(y_labels) ,high=max(y_labels))

# prepare the figure
plot = figure(plot_width=1200, plot_height=850, 
           tools=[hover, 'pan', 'wheel_zoom', 'box_zoom', 'reset', 'save', 'tap'], 
           title="Clustering of the EHR Literature with t-SNE and K-Means", 
           toolbar_location="above")

# plot settings
plot.scatter('x', 'y', size=5, 
          source=source,
          fill_color=mapper,
          line_alpha=0.3,
          line_color="black",
          legend = 'labels')
plot.legend.background_fill_alpha = 0.6

text_banner = Paragraph(text= 'Keywords: Slide to specific cluster to see the keywords.', height=45)
input_callback_1 = input_callback(plot, source, text_banner, topics)

# currently selected article
div_curr = Div(text="""Click on a plot to see the link to the article.""",height=150)
callback_selected = CustomJS(args=dict(source=source, current_selection=div_curr), code=selected_code())
taptool = plot.select(type=TapTool)
taptool.callback = callback_selected

# WIDGETS
slider = Slider(start=0, end=15, value=15, step=1, title="Cluster #")
slider.js_on_change('value', input_callback_1)
keyword = TextInput(title="Search:")
keyword.js_on_change('value', input_callback_1)

# pass call back arguments
input_callback_1.args["text"] = keyword
input_callback_1.args["slider"] = slider

# STYLE
slider.sizing_mode = "stretch_width"
slider.margin=15

keyword.sizing_mode = "scale_both"
keyword.margin=15

div_curr.style={'color': '#BF0A30', 'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif;', 'font-size': '1.1em'}
div_curr.sizing_mode = "scale_both"
div_curr.margin = 20

text_banner.style={'color': '#0269A4', 'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif;', 'font-size': '1.1em'}
text_banner.sizing_mode = "scale_both"
text_banner.margin = 20

plot.sizing_mode = "scale_both"
plot.margin = 5

r = row(div_curr,text_banner)
r.sizing_mode = "stretch_width"

# LAYOUT OF THE PAGE
l = layout([
    [slider, keyword],
    [text_banner],
    [div_curr],
    [plot],
])
l.sizing_mode = "scale_both"

# show
output_file('t-sne_ehr_interactive.html')
show(l)