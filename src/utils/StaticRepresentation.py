import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Union
import random
import io
import base64
import pandas as pd


class StaticRepresentation:
    def __init__(self):
        """Initialize the MatplotlibRepresentation class."""
        self.fig, self.ax = plt.subplots()


    def show(self):
        """Show the plot."""
        plt.show()
        

    def save_base64(self):
        """Save the plot as a base64 string."""
        buffered = io.BytesIO()
        self.fig.savefig(buffered, format="png")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    

    def create_gantt_chart(self, data: pd.DataFrame) -> str:
        """
        Create a Gantt chart and return it as a base64 string.

        Parameters:
        data (pd.DataFrame): DataFrame containing 'Ruta', 'Hora Inicio', and 'Hora Fin' columns.
        title (str): Title of the chart.
        x_label (str): Label for the X-axis.
        y_label (str): Label for the Y-axis.

        Returns:
        str: Base64 string of the Gantt chart image.
        """
        # Convert start and end times to datetime format
        data = data.copy()  # Ensure we're working with a copy of the DataFrame
        data.loc[:, 'Hora Inicio'] = pd.to_datetime(data['Hora Inicio'], format='%H:%M:%S')
        data.loc[:, 'Hora Fin'] = pd.to_datetime(data['Hora Fin'], format='%H:%M:%S')

        # Create a new column with the duration of each route
        data.loc[:, 'Duracion'] = data['Hora Fin'] - data['Hora Inicio']

        # Create the Gantt chart
        colors = plt.cm.tab20.colors  # Use a colormap for better color variety
        self.ax.set_facecolor('#EFEAE4')  # Set the background color of the plot
        bar_height = 0.85  # Fixed height for the bars
        for i, row in data.iterrows():
            self.ax.barh(row['Ruta'], row['Duracion'].total_seconds() / 3600, 
                    left=row['Hora Inicio'].hour + row['Hora Inicio'].minute / 60,
                    color=colors[i % len(colors)], edgecolor='black', height=bar_height)
            # Add the route number to each bar
            self.ax.text(row['Hora Inicio'].hour + row['Hora Inicio'].minute / 60 + row['Duracion'].total_seconds() / 7200, 
                    row['Ruta'], f'Ruta {row["Ruta"]}', va='center', ha='center', color='white', fontsize=9, fontweight='bold')

        self.ax.set_xlabel('Hora del día', fontsize=12)
        # self.ax.set_ylabel('Ruta', fontsize=12, labelpad=20)  # Increase label padding for better readability
        self.ax.set_title('Horas de Inicio y Fin de cada Ruta', fontsize=14, fontweight='bold')
        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5)

        # Format the x-axis labels
        plt.tight_layout()

        # Save the plot as a base64 string
        img_str = self.save_base64()
        plt.close(self.fig)  # Close the figure to free memory
        return img_str

    def create_line_plot(self, x_data: List[Union[int, float]], y_data: List[Union[int, float]], title: str = "Line Plot", x_label: str = "X-axis", y_label: str = "Y-axis") -> None:
        """
        Create a line plot.

        Parameters:
        x_data (List[Union[int, float]]): Data for the X-axis.
        y_data (List[Union[int, float]]): Data for the Y-axis.
        title (str): Title of the plot.
        x_label (str): Label for the X-axis.
        y_label (str): Label for the Y-axis.
        """
        self._initialize_figure()
        self.ax.plot(x_data, y_data, marker='o')
        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.show()

    def create_bar_chart(self, categories: List[str], values: List[Union[int, float]], title: str = "Bar Chart", x_label: str = "Categories", y_label: str = "Values") -> None:
        """
        Create a bar chart.

        Parameters:
        categories (List[str]): Categories for the X-axis.
        values (List[Union[int, float]]): Values for the Y-axis.
        title (str): Title of the chart.
        x_label (str): Label for the X-axis.
        y_label (str): Label for the Y-axis.
        """
        self._initialize_figure()
        self.ax.bar(categories, values)
        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.show()

    def create_scatter_plot(self, x_data: List[Union[int, float]], y_data: List[Union[int, float]], title: str = "Scatter Plot", x_label: str = "X-axis", y_label: str = "Y-axis") -> None:
        """
        Create a scatter plot.

        Parameters:
        x_data (List[Union[int, float]]): Data for the X-axis.
        y_data (List[Union[int, float]]): Data for the Y-axis.
        title (str): Title of the plot.
        x_label (str): Label for the X-axis.
        y_label (str): Label for the Y-axis.
        """
        self._initialize_figure()
        self.ax.scatter(x_data, y_data)
        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.show()

    def create_pie_chart(self, labels: List[str], values: List[Union[int, float]], title: str = "Pie Chart") -> None:
        """
        Create a pie chart.

        Parameters:
        labels (List[str]): Labels for the pie chart.
        values (List[Union[int, float]]): Values for the pie chart.
        title (str): Title of the chart.
        """
        self._initialize_figure()
        self.ax.pie(values, labels=labels, autopct='%1.1f%%')
        self.ax.set_title(title)
        self.show()

    def create_histogram(self, data: List[Union[int, float]], title: str = "Histogram", x_label: str = "X-axis", y_label: str = "Frequency") -> None:
        """
        Create a histogram.

        Parameters:
        data (List[Union[int, float]]): Data for the histogram.
        title (str): Title of the histogram.
        x_label (str): Label for the X-axis.
        y_label (str): Label for the Y-axis.
        """
        self._initialize_figure()
        self.ax.hist(data, bins=20)
        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.show()

    def create_heatmap(self, data: List[List[Union[int, float]]], x_labels: List[str], y_labels: List[str], title: str = "Heatmap", x_label: str = "X-axis", y_label: str = "Y-axis") -> None:
        """
        Create a heatmap.

        Parameters:
        data (List[List[Union[int, float]]]): Data for the heatmap.
        x_labels (List[str]): Labels for the X-axis.
        y_labels (List[str]): Labels for the Y-axis.
        title (str): Title of the heatmap.
        x_label (str): Label for the X-axis.
        y_label (str): Label for the Y-axis.
        """
        self._initialize_figure()
        sns.heatmap(data, xticklabels=x_labels, yticklabels=y_labels, ax=self.ax)
        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.show()

    def create_box_plot(self, data: List[Union[int, float]], title: str = "Box Plot", y_label: str = "Y-axis") -> None:
        """
        Create a box plot.

        Parameters:
        data (List[Union[int, float]]): Data for the box plot.
        title (str): Title of the box plot.
        y_label (str): Label for the Y-axis.
        """
        self._initialize_figure()
        self.ax.boxplot(data)
        self.ax.set_title(title)
        self.ax.set_ylabel(y_label)
        self.show()

    def create_violin_plot(self, data: List[Union[int, float]], title: str = "Violin Plot", y_label: str = "Y-axis") -> None:
        """
        Create a violin plot.

        Parameters:
        data (List[Union[int, float]]): Data for the violin plot.
        title (str): Title of the violin plot.
        y_label (str): Label for the Y-axis.
        """
        self._initialize_figure()
        sns.violinplot(data=data, ax=self.ax)
        self.ax.set_title(title)
        self.ax.set_ylabel(y_label)
        self.show()

    def create_bubble_chart(self, x_data: List[Union[int, float]], y_data: List[Union[int, float]], size_data: List[Union[int, float]], title: str = "Bubble Chart", x_label: str = "X-axis", y_label: str = "Y-axis") -> None:
        """
        Create a bubble chart.

        Parameters:
        x_data (List[Union[int, float]]): Data for the X-axis.
        y_data (List[Union[int, float]]): Data for the Y-axis.
        size_data (List[Union[int, float]]): Data for the size of the bubbles.
        title (str): Title of the bubble chart.
        x_label (str): Label for the X-axis.
        y_label (str): Label for the Y-axis.
        """
        self._initialize_figure()
        self.ax.scatter(x_data, y_data, s=size_data)
        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.show()

    def create_area_chart(self, x_data: List[Union[int, float]], y_data: List[Union[int, float]], title: str = "Area Chart", x_label: str = "X-axis", y_label: str = "Y-axis") -> None:
        """
        Create an area chart.

        Parameters:
        x_data (List[Union[int, float]]): Data for the X-axis.
        y_data (List[Union[int, float]]): Data for the Y-axis.
        title (str): Title of the area chart.
        x_label (str): Label for the X-axis.
        y_label (str): Label for the Y-axis.
        """
        self._initialize_figure()
        self.ax.fill_between(x_data, y_data)
        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.show()

if __name__ == '__main__':
    matplotlib_rep = StaticRepresentation()
    
    # More complex data for line plot and scatter plot
    x_data = [i for i in range(1, 101)]
    y_data = [i**2 for i in x_data]
    
    # More complex data for bar chart
    categories = [f'Category {i}' for i in range(1, 21)]
    values = [i * 5 for i in range(1, 21)]
    
    # More complex data for pie chart
    labels = [f'Segment {i}' for i in range(1, 11)]
    values_pie = [i * 10 for i in range(1, 11)]
    
    # More complex data for histogram
    histogram_data = [i % 10 for i in range(1, 101)]
    
    # More complex data for heatmap
    z_data = [[i * j for j in range(1, 11)] for i in range(1, 11)]
    x_labels = [f'X{i}' for i in range(1, 11)]
    y_labels = [f'Y{i}' for i in range(1, 11)]

    # Data for new plots
    y_data_box_violin = [random.gauss(0, 1) for _ in range(100)]
    size_data_bubble = [random.randint(10, 100) for _ in range(100)]

    matplotlib_rep.create_line_plot(x_data, y_data)
    matplotlib_rep.create_bar_chart(categories, values)
    matplotlib_rep.create_scatter_plot(x_data, y_data)
    matplotlib_rep.create_pie_chart(labels, values_pie)
    matplotlib_rep.create_histogram(histogram_data)
    matplotlib_rep.create_heatmap(z_data, x_labels, y_labels)
    matplotlib_rep.create_box_plot(y_data_box_violin)
    matplotlib_rep.create_violin_plot(y_data_box_violin)
    matplotlib_rep.create_bubble_chart(x_data, y_data, size_data_bubble)
    matplotlib_rep.create_area_chart(x_data, y_data)