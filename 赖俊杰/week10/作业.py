import numpy
import scipy.special
class MyNetWork:
    def __init__(self,inputnodes,hiddennodes,outputnodes,learningrate):
        self.inodes = inputnodes
        self.onodes = outputnodes
        self.hnodes = hiddennodes
        self.lr = learningrate
        self.wih = (numpy.random.normal(0.0,pow(self.hnodes,-0.5),(self.hnodes,self.inodes)))
        self.who = (numpy.random.normal(0.0,pow(self.onodes,-0.5),(self.hnodes,self.inodes)))
        self.activationo_function = lambda x:scipy.special.expit(x)
        pass
    def train(self,inputs_list,targets_list):
        inputs = numpy.array(inputs_list,ndmin=2).T
        targets = numpy.array(targets_list, ndmin=2).T
        hidden_inputs = numpy.dot(self.wih,inputs)
        hidden_outputs = self.activationo_function(hidden_inputs)
        final_inputs = numpy.dot(self.who, hidden_outputs)
        final_outputs = self.activation_function(final_inputs)
        output_errors = targets - final_outputs
        hidden_errors = numpy.dot(self.who.T, output_errors * final_outputs * (1 - final_outputs))
        self.who += self.lr * numpy.dot((output_errors * final_outputs * (1 - final_outputs)),
                                        numpy.transpose(hidden_outputs))
        self.wih += self.lr * numpy.dot((hidden_errors * hidden_outputs * (1 - hidden_outputs)),
                                        numpy.transpose(inputs))
        pass
    def query(self,inputs):
        hidden_inputs = numpy.dot(self.wih, inputs)
        hidden_outputs = self.activation_function(hidden_inputs)
        final_inputs = numpy.dot(self.who, hidden_outputs)
        final_outputs = self.activation_function(final_inputs)
        print(final_outputs)
        return final_outputs
input_nodes = 784
hidden_nodes = 200
output_nodes = 10
learning_rate = 0.1
n = MyNetWork(input_nodes, hidden_nodes, output_nodes, learning_rate)
training_data_file = open("dataset/mnist_train.csv",'r')
training_data_list = training_data_file.readlines()
training_data_file.close()
epochs = 5
for e in range(epochs):
    for record in training_data_list:
        all_values = record.split(',')
        inputs = (numpy.asfarray(all_values[1:]))/255.0 * 0.99 + 0.01
        targets = numpy.zeros(output_nodes) + 0.01
        targets[int(all_values[0])] = 0.99
        n.train(inputs, targets)
test_data_file = open("dataset/mnist_test.csv")
test_data_list = test_data_file.readlines()
test_data_file.close()
scores = []
for record in test_data_list:
    all_values = record.split(',')
    correct_number = int(all_values[0])
    print("该图片对应的数字为:",correct_number)
    inputs = (numpy.asfarray(all_values[1:])) / 255.0 * 0.99 + 0.01
    outputs = n.query(inputs)
    label = numpy.argmax(outputs)
    print("网络认为图片的数字是：", label)
    if label == correct_number:
        scores.append(1)
    else:
        scores.append(0)
print(scores)
scores_array = numpy.asarray(scores)
print("perfermance = ", scores_array.sum() / scores_array.size)
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
x_data=np.linspace(-0.5,0.5,200)[:,np.newaxis]
noise=np.random.normal(0,0.02,x_data.shape)
y_data=np.square(x_data)+noise
x=tf.placeholder(tf.float32,[None,1])
y=tf.placeholder(tf.float32,[None,1])
Weights_L1=tf.Variable(tf.random_normal([1,10]))
biases_L1=tf.Variable(tf.zeros([1,10]))
Wx_plus_b_L1=tf.matmul(x,Weights_L1)+biases_L1
L1=tf.nn.tanh(Wx_plus_b_L1) 
Weights_L2=tf.Variable(tf.random_normal([10,1]))
biases_L2=tf.Variable(tf.zeros([1,1]))  
Wx_plus_b_L2=tf.matmul(L1,Weights_L2)+biases_L2
prediction=tf.nn.tanh(Wx_plus_b_L2) 
loss=tf.reduce_mean(tf.square(y-prediction))
train_step=tf.train.GradientDescentOptimizer(0.1).minimize(loss)
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    for i in range(2000):
        sess.run(train_step,feed_dict={x:x_data,y:y_data})
    prediction_value=sess.run(prediction,feed_dict={x:x_data})
    plt.figure()
    plt.scatter(x_data,y_data)
    plt.plot(x_data,prediction_value,'r-',lw=5) 
    plt.show()
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision
import torchvision.transforms as transforms
class Model:
    def __init__(self, net, cost, optimist):
        self.net = net
        self.cost = self.create_cost(cost)
        self.optimizer = self.create_optimizer(optimist)
        pass
    def create_cost(self, cost):
        support_cost = {
            'CROSS_ENTROPY': nn.CrossEntropyLoss(),
            'MSE': nn.MSELoss()
        }
        return support_cost[cost]
    def create_optimizer(self, optimist, **rests):
        support_optim = {
            'SGD': optim.SGD(self.net.parameters(), lr=0.1, **rests),
            'ADAM': optim.Adam(self.net.parameters(), lr=0.01, **rests),
            'RMSP':optim.RMSprop(self.net.parameters(), lr=0.001, **rests)
        }
        return support_optim[optimist]
    def train(self, train_loader, epoches=3):
        for epoch in range(epoches):
            running_loss = 0.0
            for i, data in enumerate(train_loader, 0):
                inputs, labels = data
                self.optimizer.zero_grad()
                # forward + backward + optimize
                outputs = self.net(inputs)
                loss = self.cost(outputs, labels)
                loss.backward()
                self.optimizer.step()
                running_loss += loss.item()
                if i % 100 == 0:
                    print('[epoch %d, %.2f%%] loss: %.3f' %
                          (epoch + 1, (i + 1)*1./len(train_loader), running_loss / 100))
                    running_loss = 0.0
        print('Finished Training')
    def evaluate(self, test_loader):
        print('Evaluating ...')
        correct = 0
        total = 0
        with torch.no_grad():  # no grad when test and predict
            for data in test_loader:
                images, labels = data
                outputs = self.net(images)
                predicted = torch.argmax(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        print('Accuracy of the network on the test images: %d %%' % (100 * correct / total))
def mnist_load_data():
    transform = transforms.Compose(
        [transforms.ToTensor(),
         transforms.Normalize([0,], [1,])])
    trainset = torchvision.datasets.MNIST(root='./data', train=True,
                                            download=True, transform=transform)
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=32,
                                              shuffle=True, num_workers=2)
    testset = torchvision.datasets.MNIST(root='./data', train=False,
                                           download=True, transform=transform)
    testloader = torch.utils.data.DataLoader(testset, batch_size=32,shuffle=True, num_workers=2)
    return trainloader, testloader
class MnistNet(torch.nn.Module):
    def __init__(self):
        super(MnistNet, self).__init__()
        self.fc1 = torch.nn.Linear(28*28, 512)
        self.fc2 = torch.nn.Linear(512, 512)
        self.fc3 = torch.nn.Linear(512, 10)
    def forward(self, x):
        x = x.view(-1, 28*28)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.softmax(self.fc3(x), dim=1)
        return x
if __name__ == '__main__':
    # train for mnist
    net = MnistNet()
    model = Model(net, 'CROSS_ENTROPY', 'RMSP')
    train_loader, test_loader = mnist_load_data()
    model.train(train_loader)
    model.evaluate(test_loader)
