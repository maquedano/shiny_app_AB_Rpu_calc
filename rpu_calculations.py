import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu
import matplotlib.ticker as mtick


"""
Class where all the calculations are encapulated. 
Frenquentist calculations for RPU are based on Mann–Whitney U test (https://en.wikipedia.org/wiki/Mann%E2%80%93Whitney_U_test)
"""
class rpuCalculations(object):
    def __init__(self):
        """
        Initialize the object.
        """
        return
    
        
    def read_csv(self, csv_file):
        """
        Reads a CSV file and stores the data in the dataframe df

        :param csv_file: the path to the CSV file to be read
        :type csv_file: str
        """
        self.df = pd.read_csv(csv_file)

    def calculate_frequentist_result(self, percent_traffic_in_test, test_duration):
        # Calculate Mann-Whitney U statistic and p-value
        statistic, self.p_value = mannwhitneyu(
            self.df.iloc[:, 0], self.df.iloc[:, 1],
            alternative='two-sided', use_continuity=True, nan_policy='omit'
        )
        # Calculate mean of group A and group B
        self.RPU_A = self.df.iloc[:, 0].mean()
        self.RPU_B = self.df.iloc[:, 1].mean()
        # Calculate standard deviation of group A and group B
        self.std_A = self.df.iloc[:, 0].std()
        self.std_B = self.df.iloc[:, 1].std()
        # Calculate uplift
        self.uplift = self.RPU_B / self.RPU_A - 1
        # Calculate confidence level
        self.conf_level = 1 - self.p_value
        # Convert six months into days
        six_months_in_days = 182.5
        # Calculate number of users in group A and group B
        self.users_A = self.df.iloc[:, 0].count()
        self.users_B = self.df.iloc[:, 1].count()
        # Calculate visitors in six months
        visitors_in_six_months = int(
            (self.users_A + self.users_B) / (percent_traffic_in_test / 100) / test_duration * six_months_in_days
        )
        # Calculate contribution
        self.contribution = visitors_in_six_months * round(self.RPU_A, 2) * round(self.uplift, 4)


    def plot_data_distributions(self):
      """
      Plot the data distributions of two columns in the dataframe and customize the plot appearance.
      """
      fig, ax = plt.subplots(1,2, figsize=(10, 4), dpi=75)
      
      sns.kdeplot(self.df.iloc[:, 0], color="#da6d75", ax=ax[0], fill=True).set(xlabel=None)
      b = sns.kdeplot(self.df.iloc[:, 1], color="#51c4a8", ax=ax[1], fill=True)
      b.set(xlabel=None)
      b.set(ylabel=None)
      ax[0].yaxis.set_major_formatter(mtick.PercentFormatter(1))
      ax[1].yaxis.set_major_formatter(mtick.PercentFormatter(1))
      ax[0].tick_params(axis="y", colors="#595959")
      ax[0].tick_params(axis='x', colors='#595959')
      ax[1].tick_params(axis="y", colors="#595959")
      ax[1].tick_params(axis='x', colors='#595959')

      ax[0].legend(labels=["distribution A"], loc = "lower center", bbox_to_anchor=(0.5, -0.4), ncol=1, frameon=False, handleheight=1.25, handlelength=1)
      ax[1].legend(labels=["distribution B"], loc = "lower center", bbox_to_anchor=(0.5, -0.4), ncol=1, frameon=False, handleheight=1.25, handlelength=1)
      
      for spine in ax[0].spines.values():
          spine.set_edgecolor('#595959')
      
      for spine in ax[1].spines.values():
          spine.set_edgecolor('#595959')
      
      fig.tight_layout()

