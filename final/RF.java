import java.awt.*;
import java.io.*;
import java.util.*;
import javax.swing.*;

import weka.classifiers.Classifier;
import weka.classifiers.Evaluation;
import weka.core.*;
import weka.core.converters.ArffLoader;
import weka.filters.Filter;
import weka.filters.unsupervised.attribute.StringToWordVector;
import weka.classifiers.trees.RandomForest;
import java.util.Random;
import weka.classifiers.evaluation.ThresholdCurve;
import weka.gui.visualize.*;

public class RF {
	public static final String DATA_SET_FILENAME="Autism-Child-Data.arff";
	public static Instances getDataSet(String fileName) throws IOException {
		ArffLoader loader = new ArffLoader();
		loader.setSource(RF.class.getResourceAsStream("/" + fileName));
		Instances dataSet = loader.getDataSet();
		dataSet.setClassIndex(dataSet.numAttributes() - 1);
		return dataSet;
	}

	public static void main(String args[]) {
		try{
			/*
			 * cross validation
			 */
			Instances dataset = getDataSet(DATA_SET_FILENAME);
			RandomForest forest = new RandomForest();
			forest.setNumTrees(10);
			Evaluation eval = new Evaluation(dataset);
			eval.crossValidateModel(forest, dataset, 10, new Random(1));

			//System.out.println(eval.toSummaryString());
			System.out.println(eval.toMatrixString());
			System.out.println(eval.toClassDetailsString());


			/* 
			 * get roc curve
			 */
			ThresholdCurve tc = new ThresholdCurve();
			int classIndex = 1;
			Instances result = tc.getCurve(eval.predictions(), classIndex);

			ThresholdVisualizePanel vmc = new ThresholdVisualizePanel();
			vmc.setROCString("(Area under ROC = " + Utils.doubleToString(tc.getROCArea(result), 4) + ")");
			vmc.setName(result.relationName());
			PlotData2D tempd = new PlotData2D(result);
			tempd.setPlotName(result.relationName());
			tempd.addInstanceNumberAttribute();
			boolean[] cp = new boolean[result.numInstances()];
			for (int n = 1; n < cp.length; n++) {
				cp[n] = true;
			}

			tempd.setConnectPoints(cp);
			vmc.addPlot(tempd);

			String plotName = vmc.getName();
			final javax.swing.JFrame jf = new javax.swing.JFrame("Weka Classifier Visualize: "+plotName);
			jf.setSize(500,400);
			jf.getContentPane().setLayout(new BorderLayout());
			jf.getContentPane().add(vmc, BorderLayout.CENTER);
			jf.addWindowListener(new java.awt.event.WindowAdapter() {
				public void windowClosing(java.awt.event.WindowEvent e) {
					jf.dispose();
				}
			});

			jf.setVisible(true);

			/* 
			 * build model and predict
			 */
			dataset.randomize(new Random(2));
			if (dataset.classAttribute().isNominal()) {
				dataset.stratify(10);
			}
			Instances train = dataset.trainCV(10, 0);
			Instances test = dataset.testCV(10, 0);
			forest.buildClassifier(train);
			eval.evaluateModel(forest, test);
			System.out.println("=======================one-split prediction=======================");
			System.out.println(eval.toSummaryString());
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}