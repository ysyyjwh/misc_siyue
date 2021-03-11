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